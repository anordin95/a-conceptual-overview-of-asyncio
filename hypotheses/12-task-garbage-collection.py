import asyncio

async def hello():
    await asyncio.sleep(1)
    print("hello!")

async def main():
    hello_task = asyncio.create_task(hello())

asyncio.run(main())
