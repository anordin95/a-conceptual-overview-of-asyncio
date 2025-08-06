import time
import asyncio

async def coro5(x: int):
    return x + 1

async def coro4(x: int):
    return await asyncio.Task(coro5(x)) + 1

async def coro3(x: int):
    return await asyncio.Task(coro4(x)) + 1

async def coro2(x: int):
    return await asyncio.Task(coro3(x)) + 1

async def coro1(x: int):
    return await asyncio.Task(coro2(x)) + 1

async def main():
    for _ in range(10_000):
        output = await asyncio.Task(coro1(7))
    return output

start = time.perf_counter()
val = asyncio.run(main())
end = time.perf_counter()
print(f"Time elapsed: {end - start:.5f}s.")