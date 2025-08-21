This directory exists for observing the performance scaling characteristics of `await coroutine` and `await task`.

Comparing `task-perf-1-x.py` to the various other `task-perf-*.py` files shows that it's not the depth of the `await` 
so much as the number of `await`'s. In other words, it's not the call stack, it's the event loop.

`task-perf-1-x.py` awaits tasks in a non-nested way whereas the `task-perf-2.py`, `task-perf-4.py`, etc. await tasks in a nested manner. So, any difference in performance between the two approaches should *roughly* come down to call stack traversal time. And `task-perf-1-x.py`'s execution time should roughly be the time for the event loop to do it's processing *plus* the negligible time for Python to run the relatively simple code. 

To ensure the time for Python to run that code is actually negligible, there's a script `no-async-8.py` which performs the same logic with regular Python, that is no usage of asyncio nor coroutines. The runtime of that script is 0.0021s. Compared to the runtimes below, I think it's safe to assume that is indeed negligible. 

| Num Tasks | Nested | Non-Nested |
|-----------|--------|------------|
| 2         | 0.89s  | 0.61s      |
| 4         | 1.48s  | 1.21s      |
| 8         | 2.66s  | 2.39s      |

You can basically think of "Num Tasks" as the number of times the program yields to the event loop. Comparing the runtimes of the non-nested approach and the nested approach shows how the event-loop processing rather than callstack traversal largely dominates the runtime. 

One odd thing to note is that the performance drag of traversing the callstack seems roughly constant, rather than linear, as the call stack depth increases. I'm not sure why that is! 