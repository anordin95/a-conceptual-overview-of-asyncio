# Conceputal Overview Part 1: A Mental Model

## Event Loop

Everything in asyncio happens relative to the event-loop. 
It's the star of the show and there's only one. 
It's kind of like an orchestra conductor or military general. 
She's behind the scenes managing resources. 
Some power is explicitly granted to her, but a lot of her ability to get 
things done comes from the respect & cooperation of her subordinates.

In more technical terms, the event-loop contains a queue of tasks (think: "jobs", 
"work-orders", etc.) to be run. 
Some tasks are added directly by you, and some indirectly by asyncio. 
The event-loop pops a task from the queue and invokes it (or gives it control),
similar to calling a function. 
That task then runs. 
Once it pauses or completes, it returns control to the event-loop.
The event-loop then pops and invokes the next task in its queue. 
This process repeats indefinitely. 
If there are no more jobs pending execution, the event-loop is smart enough to
rest and avoid needlessly wasting CPU cycles, and will come back when there's 
more work to be done.

Effective overall execution relies on tasks sharing well. 
A greedy task could hog control and leave the other tasks to starve rendering 
the overall event-loop approach rather useless. 

```python
import asyncio

# This creates an event-loop and indefinitely cycles through its queue of tasks.
event_loop = asyncio.new_event_loop()
event_loop.run_forever()
```

## Asynchronous Functions & Coroutines

This is a regular 'ol Python function.

```python
def hello_printer():
    print(
        "Hi, I am a lowly, simple printer, though I have all I "
        "need in life -- fresh paper & a loving octopus-wife."
    )
```

Calling a regular function invokes its logic or body. 
```python
>>> hello_printer()
Hi, I am a lowly, simple printer, though I have all I need in life -- fresh paper & a loving octopus-wife.
>>>
```

This is an asynchronous function (or "coroutine function"). 
The difference between this and a regular Python function is the "async" 
keyword before the "def".

```python
async def special_fella(magic_number: int):
    print(
        "I am a super special function. Far cooler than that printer. By the way, 
        f"my lucky number is: {magic_number}."
    )
```

Calling an asynchronous function creates and returns a coroutine object. It does not execute the function.
```python
>>> special_fella(magic_number=3)
<coroutine object special_fella at 0x104ed2740>
>>> 
```

The terms "asynchronous function" (or "coroutine function") and "coroutine object" are often conflated as coroutine. 
I find that a tad confusing. 
In this article, coroutine will exclusively mean "coroutine object" -- the thing produced by executing a coroutine function.

That coroutine represents the function's body or logic. A coroutine has to be explicitly started; again, merely creating the coroutine does not start it. Notably, the coroutine can be paused & resumed at various points within the function's body. That pausing & resuming ability is what allows
for asynchronous behavior!

Coroutines and coroutine functions were built into the Python language by
building on top of the scaffoling of generators and generator functions.
Recall, a generator function is a function that yields, like this
one:

```python
def get_random_number():
    # This would be a bad random number generator!
    print("Hi")
    yield 1
    print("Howdy")
    yield 7
```

Just like a coroutine function, calling a generator function does not run it.
Instead, it creates a generator object:

```python
>>> get_random_number()
<generator object get_random_number at 0x1048671c0>
>>>
```

You can invoke/resume a generator by using the built in function `next`. 
This will proceed to the next yield in the generator, at which point 
the generator pauses. Alternatively, if there are no further yields, 
the generator ends and raises a `StopIteration` exception.

```python
>>> generator = get_random_number()
>>> next(generator)
Hi
1
>>> next(generator)
Howdy
7
>>> next(generator)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration

```

## Tasks

Roughly speaking, tasks are coroutines tied to an event-loop. A task also maintains a list of callback functions whose importance will become clear in a moment when we discuss `await`. When tasks are created they are automatically added to the event-loop's queue of tasks.

```python
# This creates a Task object.
super_special_task = asyncio.Task(coro=special_fella(magic_number=5), loop=event_loop)
```

It's common to see a task instantiated without explicitly specifying the event-loop it belongs to. Since there's only one event-loop (a global singleton), asyncio made the loop argument optional and will add it for you if it's left unspecified.
```python
# The task is implicitly tied to the event-loop by asyncio since the loop 
# argument was left unspecified.
another_super_special_task = asyncio.Task(coro=special_fella(magic_number=12))
```

After those two statements are executed, the event-loop should have two corresponding tasks or jobs in its queue.

`asyncio.Task` is considered the low-level API for task creation. The recommended,
higher-level interface is `asyncio.create_task`. 
In my experience they're quite similar, but `asyncio.Task` has more bells and whistles you can play with. 
As the blessed, recommended interface `asyncio.create_task` will likely be
a far more stable interface over time. 
That is, as `asyncio` evolves, the authors/editors will work hard to ensure `asyncio.create_task`'s behavior doesn't change.

```python
# Yet another task.
one_last_task = asyncio.create_task(special_fella(magic_number=7))
```

Earlier, we manually created the event loop and set it to run forever.
In practice, it's recommended to use (and common to see) `asyncio.run`
which takes care of managing the event loop and ensuring the provided
coroutine finishes before advancing.
For example, many async programs follow this setup:

```python
import asyncio

async def main():
    # Perform all sorts of wacky, wild asynchronous things...
    ...

if __name__ == "__main__":
    asyncio.run(main())
    # The program will not reach the following print statement until the
    # coroutine main() finishes.
    print("coroutine main() is done!")
```

## `await`

await is a Python keyword that's commonly used in one of two different ways:

```python
await coroutine
await task
```

Unfortunately, it actually does matter which type of object await is applied to. 

Awaiting a task will cede control from the current task or coroutine to
the event loop.
In the process of relinquishing control, a few important things happen.
We'll use the following code example to illustrate:

```python
async def plant_a_tree():
    dig_the_hole_task = asyncio.create_task(dig_the_hole())
    await dig_the_hole_task

    # Other instructions/code associated with planting a tree...
    ...
```

For reference, when I say `plant_a_tree` I'm referring to the coroutine function. And `plant_a_tree()` refers to a coroutine object made from that coroutine function.

In this example, imagine the event loop has passed control to the start of the
coroutine `plant_a_tree()`.
As seen above, the coroutine creates a task and then awaits it.
The `await dig_the_hole_task` instruction adds a callback (which will resume
`plant_a_tree()`) to the `dig_the_hole_task` object's list of callbacks.
And then, the instruction cedes control to the event loop.
Some time later, the event loop will pass control to `dig_the_hole_task`
and the task will finish whatever it needs to do.
Once the task finishes, it will add its various callbacks to the event loop,
in this case, a call to resume `plant_a_tree()`.

Generally speaking, when the awaited task finishes (`dig_the_hole_task`),
the original task or coroutine (`plant_a_tree()`) is added back to the event
loops to-do list to be resumed.

This is a basic, yet reliable mental model.
In practice, the control handoffs are slightly more involved, but not by much.
In part 2, we'll walk through the details that make this possible.

**Unlike tasks, await-ing a coroutine does not cede control!** Wrapping a coroutine in a task first, then await-ing that would cede control. The behavior of `await coroutine` is effectively the same as invoking a regular, synchronous Python function. Consider this program:

```python
import asyncio

async def coro_fn_a():
    print("I am coro_a(). Hi!")

async def coro_fn_b():
    print("I am coro_b(). I sure hope no one hogs the event loop...")

async def main():
    task_b = asyncio.create_task(coro_fn_b())
    num_repeats = 5
    for _ in range(num_repeats):
        coro_a = coro_fn_a()
        await coro_a
    await task_b

asyncio.run(main())
```

The first statement in the coroutine `main()` creates `task_b` and schedules it for execution via the event loop (i.e. adds it to the queue of jobs).
Then, `coro_a` is repeatedly created then awaited. Control never cedes to the event loop which is why we see the output of all five `coro_a`
invocations before `task_b`'s output:

```bash
I am coro_a(). Hi!
I am coro_a(). Hi!
I am coro_a(). Hi!
I am coro_a(). Hi!
I am coro_a(). Hi!
I am coro_b(). I sure hope no one hogs the event loop...
```

Now, if instead of awaiting `coro_a` we awaited a Task which wrapped `coro_a`, like `await asyncio.create_task(coro_a)`, we'd see:

```bash
I am coro_b(). I sure hope no one hogs the event loop...
I am coro_a(). Hi!
I am coro_a(). Hi!
I am coro_a(). Hi!
I am coro_a(). Hi!
I am coro_a(). Hi!
```

The coroutine `main()` cedes control to the event loop with that new statement.
The event loop then proceeds through its backlog of work, calling `task_b`
and then the task which wraps `coro_a()` before resuming the coroutine
`main()`.

This behavior of `await coroutine` can trip a lot of people up!
That example highlights how using only ``await coroutine`` could
unintentionally hog control from other tasks and effectively stall the event
loop.
For reference, asyncio can help you track down greedy coroutines via
the `debug=True` flag for `asyncio.run`. 
Among other things, that will log any coroutines that monopolize 
execution for 100ms or longer.

This design of `await` intentionally trades off some conceptual clarity around usage for improved performance.
Each time a task is awaited, control needs to be passed all the way up the
call stack to the event loop. 
And keep in mind, if many `await`'s are chained together, as is common in practice, each `await` must traverse the call stack each time.
That might sound minor, but in a large program with many `await`'s and a deep
callstack that overhead can add up to a meaningful performance drag.

You can play around with the programs in `hypotheses/9-await-perf-coro.py` and
`hypotheses/10-await-perf-task.py`. 
They measure the performance of each approach on a simple program many, many times. The programs recursively await a coroutine or task to a depth of 10.
That means the average callstack depth is 5, which is arguably shallower than
most real programs.
The `await task` approach takes about 3 seconds for 10,000 runs or about 300 microseconds per run.
The `await coroutine` approach takes about 7 milliseconds for 10,000 runs or about 0.7 microseconds per run. It's 430 times faster.
I know these numbers all sound extremely small to us humans, but to computers
they're a lot!
This [page of common latency numbers](https://gist.github.com/jboner/2841832) in a computer is a helpful reference point.

## Tying it together

So far you've covered a lot! Let's recap and then see how these ideas all work together.
The event loop orchestrates the whole show. You can basically think of it as a queue that runs jobs 
one at a time in the order they're provided. 
The jobs are calls to invoke/resume tasks.
Tasks are largely coroutines that are tied to an event loop.
And coroutines are like regular Python functions that can be paused and resumed throughout their body.

One classic gotcha is that the event loop does not store tasks in the queue, but callbacks which generally invoke tasks, though they can do other more general things too!
I know that sounds minor and pedantic, but it matters for garbage collection.
If you don't keep a reference to the task, there will be no references to the object, and the
garbage collector (i.e. memory cleanup) may obliterate that object and reclaim those bytes.
That's problematic if the event loop later tries to invoke the now non-existent object!

### [Next: A conceptual overview part 2: the nuts & bolts](https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/main/2-conceptual-overview-part-2.md)