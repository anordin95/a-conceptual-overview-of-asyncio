import time
import asyncio

async def coro(depth: int):
    if depth == 0:
        return 1
    else:
        return await asyncio.Task(coro(depth - 1))

async def main():
    for _ in range(10_000):
        await asyncio.Task(coro(MAX_DEPTH))

MAX_DEPTH = 30
start = time.perf_counter()
val = asyncio.run(main())
end = time.perf_counter()
print(f"Time elapsed: {end - start:.5f}s.")