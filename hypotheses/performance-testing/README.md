**This directory exists for observing the performance characteristics of `await coroutine` and `await task`.**

## Context 
`coro-perf-2.py` runs 3 coroutines. 
The first coroutine awaits the second, which awaits the third. 
The deepest `await` happens at a depth of 2, hence the 2 suffix.
The program runs those 3 coroutines 10,000 times and measures the elapesd time.
Files named `task-...` do the same thing, but with tasks instead of coroutines.

`coro-perf-1-seq.py` and `task-perf-1-seq.py` are unique. 
Instead of awaiting nested tasks, it awaits depth-one coroutines (or tasks) repeatedly.
This allows us to compare the performance of nested awaits and depth-one awaits.

To serve as a reference, there's also a script `no-async.py` which performs the same logic with no usage of asyncio nor coroutines.

## Performance

| Max Depth or Num Sequential Calls | Nested Tasks | Non-Nested Tasks | Nested Coroutines | Non-Nested Coroutines | No Async |
|-----------------------------------|--------------|------------------|-------------------|-----------------------|----------|
| 2                                 | 0.89s        | 0.61s            | 0.003s            | 0.002s                | 0.0005s  |
| 4                                 | 1.48s        | 1.21s            | 0.004s            | 0.003s                | 0.001s   |
| 8                                 | 2.66s        | 2.39s            | 0.007s            | 0.006s                | 0.002s   |


The execution time for the "Non-Nested Tasks" approach should roughly be the time for the event loop to do it's processing *plus* the time for Python to run the relatively simple code. 
Given how quickly the "Non-Nested Coroutines" and "No Async" execute, it's clear the bottleneck is the event loop's processing.
And, as we see above, increasing the number of awaits or sequential calls, linearly increases the runtime.

Comparing the "Nested Tasks" and "Non-Nested Tasks" runtimes, we see differences of 0.28s, 0.27s and 0.27s.
I believe this difference should represent the callstack traversal time.
If traversing the callstack were indeed a major factor, we should see some increase in those differences as the depth of awaits increases. 
But, we do not. 
One odd thing to note is that the performance drag of traversing the callstack seems roughly constant, rather than linear, as the call stack depth increases. I'm not sure why that is! 


