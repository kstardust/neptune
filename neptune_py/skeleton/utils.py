import asyncio
from neptune_py.skeleton.skeleton import NeptuneServiceSkeleton


class AnsiColor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def color_print(color: AnsiColor, *args):
    print(color, *args, AnsiColor.ENDC)


class Introspector(NeptuneServiceSkeleton):
    def __init__(self):
        super().__init__('Introspector')

    async def logic(self):
        while True:
            self.get_logger().debug(f'current tasks(coroutines) {len(asyncio.all_tasks())}')
            await asyncio.sleep(5)
