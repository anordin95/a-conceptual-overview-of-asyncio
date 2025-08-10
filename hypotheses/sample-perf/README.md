This directory exists for observing the performance scaling characteristics of `await coroutine` and `await task`.

Comparing task-perf-1x.py to the various other task-perf-*.py files shows that it's not the depth of the `await` 
so much as the number of `await`'s. In other words, it's not the call stack, it's the event loop.

