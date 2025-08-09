# A conceptual overview of the ideas and objects which power asyncio

## Motivation

I've used Python's asyncio a couple times now, but never really felt confident in my mental model of how it fundamentally works and therefore how I can best leverage it. The official docs provide decent documentation for each specific function in the package, but, in my opinion, lack a cohesive overview of the systems design and architecture. Something that could help the user understand the why and how behind the recommended patterns. And a way to help the user make informed decisions about which tool in the asyncio toolkit they ought to grab, or to recognize when asyncio is the entirely wrong toolkit. This is my attempt to fill that gap.

There were some articles I found online that were illuminating with certain aspects, but didn't totally cover what I was after. They're linked at the end of the final section.

During my learning process, a few aspects particually drove my curiosity (read: drove me nuts). You should be able to answer all these questions by the end of this article.
- What's roughly happening behind the scenes when an object is `await`-ed? 
- How does `asyncio` differentiate between a task which doesn't need cpu-time to make progress towards completion (for example, a network-request or file-read) as opposed to a task that does need cpu-time to make progress (for example, computing n-factorial)?
- How would I go about writing my own asynchronous variant of some operation (e.g. sleep, network-request, file-read, etc.)?

## Sections

The first two sections feature some examples but are generally focused on theory and explaining concepts. The next two sections are centered around examples, focused on further illustrating and reinforcing ideas practically. The final section compares multiprocessing, multithreading & asyncio and
describes when you'd want each one.

#### [A conceptual overview part 1: a mental model](https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/main/1-conceptual-overview-part-1.md)

In part 1, we'll cover the main, high-level building blocks of asyncio: the event-loop, coroutine functions,
coroutine objects, tasks & await. 

#### [A conceptual overview part 2: the nuts & bolts](https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/main/2-conceptual-overview-part-2.md)

Part 2 goes into detail on the mechanisms asyncio uses to manage control flow. This is where the magic happens. You'll
come away from this section knowing what await does behind the scenes and how to make your own asynchronous operators.

#### [Analyzing an example programs control flow](https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/main/3-detailed-control-flow-analysis-example.md)

We'll walkthrough, step by step, a simple asynchronous program following along in the key methods of Task & Future that are leveraged when asyncio is orchestrating the show. 

#### [Barebones network I/O example](https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/main/4-barebones-network-io-example.md)

A simple but thorough example showing how asyncio can offer an advantage over serial programs. The example doesn't rely on 
any asyncio operators (besides the event-loop). It's all non-blocking sockets & custom awaitables that help you see what's
actually happening under the hood and how you could do something similar.

#### [When to use asyncio & closing thoughts](https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/main/5-conclusions.md)

This section briefly describes and contrasts the three common approaches to concurrency and where each is most useful. 