"""
await-ing a Future cedes control to the event-loop.
"""
import asyncio
import datetime

async def auxiliary_func():
    print("Executing auxiliary_func()...")

async def main():
    
    future = asyncio.Future()
    asyncio.Task(auxiliary_func(), loop=loop)
    # Note: cannot specify loop with create_task approach.
    # asyncio.create_task(auxiliary_func())
    
    print(f"Awaiting future...")
    await future
    
    # The future is never marked as done, so this statement will
    # not be executed.
    print("Control never gets here.")


loop = asyncio.new_event_loop()
main_task = asyncio.Task(main(), loop=loop)
loop.run_until_complete(main_task)
