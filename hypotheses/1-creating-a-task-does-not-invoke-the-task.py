"""
Instantiating a task schedules it for execution. But the task won't execute
until control somehow gets back to the event-loop.
"""

import time
import asyncio

async def other_func():
    print("Executing other_func.")

async def main():
    
    task = asyncio.Task(coro=other_func())
    
    # Uncomment this line to see the effect awaiting a Task has on the order of prints.
    # await asyncio.sleep(0)

    print("hey, hi, hello!")
    time.sleep(3)
    await task

# asyncio.run(main())

loop = asyncio.new_event_loop()
import ipdb; ipdb.set_trace()
loop.run_forever()
