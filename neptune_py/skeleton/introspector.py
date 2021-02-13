import asyncio
from neptune_py.skeleton.skeleton import NeptuneServiceSkeleton


class Introspector(NeptuneServiceSkeleton):
    def __init__(self):
        super().__init__('Introspector')

    async def logic(self):
        while True:
            self.get_logger().debug(f'current tasks(coroutines) {len(asyncio.all_tasks())}')
            await asyncio.sleep(5)
