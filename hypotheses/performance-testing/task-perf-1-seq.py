import time
import asyncio


async def coro1(x: int):
    return x + 1

async def main():
    for _ in range(10_000):
        
        output = await asyncio.Task(coro1(1))
        output = await asyncio.Task(coro1(2))
        output = await asyncio.Task(coro1(3))
        output = await asyncio.Task(coro1(4))
        
        output = await asyncio.Task(coro1(5))
        output = await asyncio.Task(coro1(6))
        output = await asyncio.Task(coro1(7))
        output = await asyncio.Task(coro1(8))

    return output

start = time.perf_counter()
val = asyncio.run(main())
end = time.perf_counter()
print(f"Time elapsed: {end - start:.5f}s.")