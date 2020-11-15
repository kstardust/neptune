import asyncio

from neptune_py.skeleton.skeleton import NeptuneServerSkeleton, NeptuneServiceSkeleton
from neptune_py.skeleton.messager import NeptuneMessagerManager
from neptune_py.skeleton.neptune_rpc.neptune_wsrpc import (
    NeptuneWSService, NeptuneWSRpc
)
from neptune_py.skeleton.neptune_rpc.neptune_tlv import NeptuneTlvService, NeptuneTlvClient
from neptune_py.skeleton.entity.entity import NeptuneEntityBase
from . test_entity import TestingClientEntity


class Introspector(NeptuneServiceSkeleton):
    def __init__(self):
        super().__init__('Introspector')

    async def logic(self):
        while True:
            self.get_logger().debug(f'current tasks(coroutines) {len(asyncio.all_tasks())}')
            await asyncio.sleep(5)


class EchoEntity(NeptuneEntityBase):
    def on_message(self, message):
        print(message)
        self.messager.write_message(13, message.message)


class Neptune:
    def __init__(self, name):
        self.name = name
        self.init_services()

    def init_services(self):
        np_server = NeptuneServerSkeleton(self.name)
        # self.client_manager = NeptuneMessagerManager(TestingClientEntity)
        self.client_manager = NeptuneMessagerManager(EchoEntity)

        np_server.add_service(Introspector())
        np_server.add_service(NeptuneTlvService('0.0.0.0', '1313', self.client_manager))

        self.np_server = np_server

    async def run(self):
        async def server2():
            await asyncio.sleep(2)
            await self.np_server2.run()

        await asyncio.gather(
            self.np_server.run()
        )


if __name__ == '__main__':
    np = Neptune('neptune')
    asyncio.run(np.run())
