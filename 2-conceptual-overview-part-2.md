# Conceputal Overview Part 2: The Nuts & Bolts

## How coroutines work under the hood

`asyncio` leverages four components exposed by Python to manage and pass around control. 
For reference, coroutine functions and coroutine objects are built into Python directly, not asyncio.

`coroutine.send(arg)` is the method used to start or resume a coroutine. If the coroutine was paused and is now being resumed, the argument `arg` will be sent in as the return value of the `yield` statement which originally paused it. If the coroutine is being started, as opposed to resumed, arg must be `None`.

`yield`, like usual, pauses execution and returns control to the caller. In the example below, the yield is on line 3 and the caller is `... = await rock` on line 11. Generally, await calls the `__await__` method of the given object. await also does one more very special thing: it percolates (or passes along) any yields it receives up the call-chain. In this case, that's back to `... = coroutine.send(None)` on line 16. 

The coroutine is resumed via the `coroutine.send(42)` call on line 21. The coroutine picks back up from where it yielded (i.e. paused) on line 3 and executes the remaining statements in its body. When a coroutine finishes it raises a `StopIteration` exception with the return value attached to the exception.

```python
1   class Rock:
2       def __await__(self):
3           value_sent_in = yield 7
4           print(f"Rock.__await__ resuming with value: {value_sent_in}.")
5           return value_sent_in
6   
7   async def main():
8       print("Beginning coroutine main().")
9       rock = Rock()
10      print("Awaiting rock...")
11      value_from_rock = await rock
12      print(f"Coroutine received value: {value_from_rock} from rock.")     
13      return 23
14  
15  coroutine = main()
16  intermediate_result = coroutine.send(None)
17  print(f"Coroutine paused and returned intermediate value: {intermediate_result}.")
18   
19  print(f"Resuming coroutine and sending in value: 42.")
20  try:
21      coroutine.send(42)
22  except StopIteration as e:
23      returned_value = e.value
24  print(f"Coroutine main() finished and provided value: {returned_value}.")
```

That snippet produces this output:
```
Beginning coroutine main().
Awaiting rock...
Coroutine paused and returned intermediate value: 7.
Resuming coroutine and sending in value: 42.
Rock.__await__ resuming with value: 42.
Coroutine received value: 42 from rock.
Coroutine main() finished and provided value: 23.
```

It's worth pausing for a moment here and making sure you followed the various ways control flow and values were passed.
A lot of important ideas were covered and it’s worth ensuring your understanding is firm.

The only way to yield (or effectively cede control) from a coroutine is to await an object that `yield`s in its `__await__` method. That might sound odd to you. Frankly, it was to me too. You might be thinking:
1. What about a `yield` directly within the coroutine? The coroutine becomes an async generator, a different beast entirely.
2. What about a `yield from` within the coroutine to a function that `yield`s (i.e. plain generator)? SyntaxError: `yield from` not allowed in a coroutine.  This was intentionally designed for the sake of simplicity – mandating only one way of using coroutines. Initially yield was barred as well, but was re-accepted to allow for async generators. Despite that, yield from and await effectively do the same thing.

## Futures

A future (`asyncio.Future`) is an object meant to represent a computation or process's status and result. 
The term is a nod to the idea of something still to come or not yet happened, and the object is a way to keep an eye on that something.

A future has a few important attributes. One is its state which can be either pending, cancelled or done. Another is its result which is set when the state transitions to done. To be clear, a Future does not represent the actual computation to be done, like a coroutine does. Instead it represents the status and result of that computation, kind of like a status-light (red, yellow or green) or indicator. 

Task subclasses Future in order to gain these various capabilities. I said in the prior section tasks store a list of callbacks and I lied a bit. It's actually the Future class that implements this logic which Task inherits.

Futures may be also used directly i.e. not via tasks. Tasks mark themselves as done when their coroutine's complete. Futures are much more versatile and will be marked as done when you say so. In this way, they're the flexible interface for you to make your own conditions for waiting and resuming. Here's an example of how you could leverage Future to create your own variant of asynchronous sleep (i.e. asyncio.sleep).

## Homemade asyncio.sleep

We’ll go through an example of how you could leverage a future to create your own variant of asynchronous sleep which mimics the official asyncio.sleep().

This snippet registers a few tasks with the event loop and then awaits a coroutine wrapped in a task: async_sleep(3). We want that task to finish only after three seconds have elapsed, but without preventing other tasks from running.

```python
async def other_work():
    print("I like work. Work work.")

async def main():
    # Add a few other tasks to the event loop, so there's something
    # to do while asynchronously sleeping.
    work_tasks = [
        asyncio.create_task(other_work()),
        asyncio.create_task(other_work()),
        asyncio.create_task(other_work())
    ]
    print(
        "Beginning asynchronous sleep at time: "
        f"{datetime.datetime.now().strftime("%H:%M:%S")}."
    )
    await asyncio.create_task(async_sleep(3))
    print(
        "Done asynchronous sleep at time: "
        f"{datetime.datetime.now().strftime("%H:%M:%S")}."
    )
    # asyncio.gather effectively awaits each task in the collection.
    await asyncio.gather(*work_tasks)
```

Below, we use a future to enable custom control over when that task will be marked as done. If future.set_result() (the method responsible for marking that future as done) is never called, then this task will never finish. We’ve also enlisted the help of another task, which we’ll see in a moment, that will monitor how much time has elapsed and, accordingly, call future.set_result().

```python
async def async_sleep(seconds: float):
    future = asyncio.Future()
    time_to_wake = time.time() + seconds
    # Add the watcher-task to the event loop.
    watcher_task = asyncio.create_task(_sleep_watcher(future, time_to_wake))
    # Block until the future is marked as done.
    await future
```

We’ll use a rather bare, simple object, YieldToEventLoop(), to yield from __await__ in order to cede control to the event loop. This is effectively the same as calling asyncio.sleep(0), but this approach offers more clarity, not to mention it’s somewhat cheating to use asyncio.sleep when showcasing how to implement it!

```python
class YieldToEventLoop:
    def __await__(self):
        yield
```

Finally, we'll review the coroutine function `_sleep_watcher`. This coroutine compares the current time to `time_to_wake`. 
If it's not time for wakeup, the coroutine will cede to the event loop. If it is time to get out of bed, the coroutine will
mark the given future as done and then finish by breaking out of its infinite while loop.

```python
async def _sleep_watcher(future, time_to_wake):
    while True:
        if time.time() >= time_to_wake:
            # This marks the future as done.
            future.set_result(None)
            break
        else:
            await YieldToEventLoop()
```

Let's put this in context. As usual, the event loop cycles through its tasks, giving them control and receiving control back when they pause or finish. The `watcher_task`, which runs the coroutine `_sleep_watcher(...)`, will be invoked once per full cycle of the event loop. On each resumption, it’ll check the time and if not enough has elapsed, then it’ll pause once again and hand control back to the event loop. 

Eventually, enough time will have elapsed, and `_sleep_watcher(...)` will mark the future as done, and then itself finish too by breaking out of the infinite while loop. When the future is marked as done, it adds its callbacks to the event loops queue, in this case a call to resume `async_sleep()`. When `async_sleep()` resumes, there are no further instructions (the last one was `await future`), so it too finishes and its callbacks, one to resume `main()`, to the event loop.

Given the helper task `watcher_task` (which is tied to the coroutine `_sleep_watcher`) is only invoked once per cycle of the event loop, you’d be correct to note that this asynchronous sleep will sleep at least three seconds, rather than exactly three seconds. Note this is also of true of asyncio.sleep.

Finally, here is that program's output:
```bash
 $ python hypotheses/7-custom-async-sleep.py
Beginning asynchronous sleep at time: 14:52:22.
I am worker. Work work.
I am worker. Work work.
I am worker. Work work.
Done asynchronous sleep at time: 14:52:25.
```

You might feel this implementation of asynchronous sleep was unnecessarily convoluted. And, well, that's because it was! The example was meant to showcase the versatility of futures with a simple example that could be mimicked for more complex needs. For reference, you could implement it without futures, like so:

```python
async def simpler_async_sleep(seconds):
    time_to_wake = time.time() + seconds
    while True:
        if time.time() >= time_to_wake:
            return
        else:
            await YieldToEventLoop()
```

## `await`-ing Tasks & Futures

Future defines an important method: `__await__`. Below is the actual implementation (well, one line was removed for simplicity's sake) found in `asyncio.futures.Future`. It's okay if it doesn't make complete sense now, we'll go through it in detail in the control-flow example.

```python
1  class Future:
2      ...
3      def __await__(self):
4      
5          if not self.done():
6              yield self
7        
8          if not self.done():
9              raise RuntimeError("await wasn't used with future")
10        
11         return self.result()
```

The Task class does not override Futures `__await__` implementation. await-ing a Task or Future invokes that above `__await__` method and percolates the yield on line 6 above to relinquish control to its caller, which is generally the event-loop.

The control flow example next will examine in detail how control flow and values are passed through an example asyncio program, the event-loop, `Future.__await__` and `Task.step`. 

### [Next: Analyzing an example programs control flow](https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/main/3-detailed-control-flow-analysis-example.md)


