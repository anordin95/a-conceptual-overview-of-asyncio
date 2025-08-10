import time
import asyncio

async def coro9(x: int):
    return x + 1

async def coro8(x: int):
    return await asyncio.Task(coro9(x)) + 1

async def coro7(x: int):
    return await asyncio.Task(coro8(x)) + 1

async def coro6(x: int):
    return await asyncio.Task(coro7(x)) + 1

async def coro5(x: int):
    return await asyncio.Task(coro6(x)) + 1

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