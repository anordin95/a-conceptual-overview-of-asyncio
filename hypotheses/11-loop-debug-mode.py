import asyncio

async def compute_factorial(n: int):
    total = 1
    for num in range(1, n + 1):
        total *= num

async def main():
    await compute_factorial(n=50_000)


asyncio.run(main(), debug=True)