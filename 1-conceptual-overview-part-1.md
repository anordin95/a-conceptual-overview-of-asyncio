# Conceputal Overview Part 1: A Mental Model

## Event Loop

Everything in asyncio happens relative to the event-loop. It's the star of the show and there's only one. It's kind of like an orchestra conductor or military general. She's behind the scenes managing resources. Some power is explicitly granted to her, but a lot of her ability to get things done comes from the respect & cooperation of her subordinates.

In more technical terms, the event-loop contains a queue of tasks to be run. Some tasks are added directly by you, and some indirectly by asyncio. The event-loop pops a task from the queue and invokes it (or gives it control), similar to calling a function. That task then runs. Once it pauses or completes, it returns control to the event-loop. The event-loop then pops and invokes the next task in its queue. This process repeats indefinitely. Even if the queue is empty, the event-loop continues to cycle (somewhat aimlessly).

Effective overall execution relies on tasks sharing well. A greedy task could hog control and leave the other tasks to starve rendering the overall event-loop approach rather useless. 

```python
import asyncio

# This creates an event-loop and indefinitely cycles through its queue of tasks.
event_loop = asyncio.new_event_loop()
event_loop.run_forever()
```

## Asynchronous Functions & Coroutines

This is a regular 'ol Python function.
```python
def simple_print():
    print(
        "Hi, I am simple_print(), a lowly, simple printer, though I have all I"
        "need in life -- fresh paper & a loving octopus-wife."
    )
```

Calling a regular function invokes its logic or body. 
```python
>>> hello_printer()
Hi, I am simple_print(), a lowly, simple printer, though I have all I need in life -- fresh paper & a loving octopus-wife.
>>>
```

This is an asynchronous-function or coroutine-function.
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

The terms "asynchronous function" (or "coroutine function") and "coroutine object" are often conflated as coroutine. I find that a tad confusing. In this article, coroutine will exclusively mean "coroutine object" -- the thing produced by executing a coroutine function.

That coroutine represents the function's body or logic. A coroutine has to be explicitly started; again, merely creating the coroutine does not start it. Notably, the coroutine can be paused & resumed at various points within the function's body. That pausing & resuming ability is what allows
for asynchronous behavior!

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

After those two statements are executed, the event-loop should have two corresponding tasks in its queue.

## `await`

await is a Python keyword that's commonly used in one of two different ways:
```python
await coroutine
await task
```

Unfortunately, it actually does matter which type of object await is applied to. 

await-ing a task will cede control to the event-loop. And while doing so, add a callback to the awaited task's list of callbacks indicating it should resume the current task when that one finishes. In practice, it's slightly more convoluted, but not by too much. In part 2, you'll walk through all the details that make this possible. And in the control flow analysis example you'll walk through, in precise detail, the various control handoffs in an example async program.

***Unlike tasks, await-ing a coroutine does not cede control!*** Wrapping a coroutine in a task first, then await-ing that would cede control. The behavior of `await coroutine` is effectively the same as invoking a regular, synchronous Python function. I'd understand if you're skeptical of this; if you don't believe it, play around with the program in `./hypotheses/4-awaiting-a-coroutine-does-not-cede-control-to-the-event-loop.py`. Frankly, I'm not sure why that design decision was made and find it rather confuses the meaning of await: asynchronously wait. I offer my opinions on an alternative approach in the final section.


```python
async def db_request():
    ...

async def main():
    
    # This will invoke db_request() without first yielding to the event-loop.
    await db_request()

    # This line does two things. First it instantiates the Task which will 
    # add it to the event-loops' queue. Then, it awaits the Task which will
    # yield control to the event-loop. Eventually, the event-loop will 
    # invoke db_request().
    await Task(coro=db_request())
```

### [Next: A conceptual overview part 2: the nuts & bolts](https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/main/2-conceptual-overview-part-2.md)
