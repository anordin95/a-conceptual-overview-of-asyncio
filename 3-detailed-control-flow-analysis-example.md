# Analyzing an example programs control flow

The actual method that invokes a Tasks coroutine: `asyncio.tasks.Task.__step_run_and_handle_result` is about 80 lines long. For the sake of clarity, I've removed all of the edge-case error handling, simplified some aspects and renamed it, but the core logic remains unchanged.

## Task

```python
1  class Task(Future):
2      ...
3      def step(self):
4          try:
5              awaited_task = self.coro.send(None)
6          except StopIteration as e:
7              super().set_result(e.value)
8          else:
9              awaited_task.add_done_callback(self.step)
10         ...
```

## Future

For ease of reference, here's the `Future.__await__` method again.
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

## Example program 
We'll analyze how control flows through this example program: `program.py` and the methods `Task.step` & `Future.__await__`.

```python
# Filename: program.py
1  async def triple(val: int):
2      return val * 3
3
4  async def main():
5      triple_task = asyncio.Task(coro=triple(val=5))
6      tripled_val = await triple_task
7      return tripled_val + 2
8
9  loop = asyncio.new_event_loop()
10 main_task = asyncio.Task(main(), loop=loop)
11 loop.run_forever()
```

## Control flow

At a high-level, this is how control flows: 

```
1  program
2      event-loop
3          main_task.step
4              program::main
5                  triple_task.__await__
6              program::main
7          main_task.step
8      event-loop
9          triple_task.step
10             program::triple
11         triple_task.step
12     event-loop
13         main_task.step
14             triple_task.__await__
15                 program::main
16         main_task.step
17     event-loop
```

And, in much more detail:

1. Control begins in **`program.py`** 
    * Line 9 creates an event-loop, line 10 creates `main_task` and adds it to the event-loop, line 11 invokes the event-loop. 
1. Control is now in the **`event-loop`**
    * The event-loop pops `main_task` off the queue then invokes it by calling `main_task.step()`. 
1. Control is now in **`main_task.step`**
    * We enter the try-block on line 4 then begin the coroutine `main` on line 5. 
1. Control is now in **`program.main`**
    * The Task `triple_task` is created on line 5 which adds it to the event-loops' queue. Line 6 awaits `triple_task`. Recall, that calls `Task.__await__` then percolates any yields.
1. Control is now in **`triple_task.__await__`**
    * `triple_task` is not done given it was just created, so we enter the first if-block on line 5 and yield the thing we'll
    be waiting for -- triple_task.
1. Control is now in **`program.main`**
    * `await` percolates the yield and the yielded value -- `triple_task`.
1. Control is now in **`main_task.step`**
    * The variable `awaited_task` is `triple_task`. No StopIteration was raised so the else in the try-block on line 8 executes. A done-callback: `main_task.step` is added to the `triple_task`. The `step` method ends and returns to the event-loop.
1. Control is now in the **`event-loop`**
    * The event-loop cycles to the next task in its queue. The event-loop pops `triple_task` from its queue and invokes it by calling `triple_task.step()`.
1. Control is now in **`triple_task.step`**
    * We enter the try-block on line 4 then begin the coroutine `triple` on line 5. 
1. Control is now in **`program.triple`**
    * Control goes to the coroutine `triple` on line 2. It computes 3 times 5, then finishes and raises a StopIteration exception.
1. Control is now in **`triple_task.step`**
    * The StopIteration exception is caught so we go to line 7. The return value of the coroutine `triple` is embedded in the `value` attribute of that exception. Future.set_result() saves the result, marks the task as done and adds the done-callbacks of `triple_task` to the event-loops' queue. The `step` method ends and returns control to the event-loop.
1. Control is now in the **`event-loop`**
    * The event-loop cycles to the next task in its queue. The event-loop pops `main_task` and resumes it by calling `main_task.step()`.
1. Control is now in **`main_task.step`**
    * We enter the try-block on line 4 then resume the coroutine `main` which will pick up again from where it yielded. Recall,
    it yielded not in the coroutine, but in `triple_task.__await__` on line 6.
1. Control is now in **`triple_task.__await__`**
    * We evaluate the if-statement on line 8 which ensures that `triple_task` was completed. Then, it returns the `result` of `triple_task` which was saved earlier. Finally that `result`
    is returned to the caller (i.e. `... = await triple_task`).
1. Control is now in **`program.main`** 
    * `tripled_val` is now 15. The coroutine finishes and raises a StopIteration exception with the return value of 17 attached.
1. Control is now in **`main-task.step`** 
    * The StopIteration exception is caught and `main_task` is marked as done and its result is saved. The `step` method ends and returns control to the event-loop.
1. Control is now in the **`event-loop`** 
    * There's nothing in the queue. The event-loop cycles aimlessly onwards.

### [Next: Barebones network I/O example](https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/main/4-barebones-network-io-example.md)
