import asyncio

from neptune_py.skeleton.skeleton import NeptuneServerSkeleton, NeptuneServiceSkeleton
from neptune_py.skeleton.messager import NeptuneMessagerManager
from neptune_py.skeleton.neptune_rpc.neptune_wsrpc import (
    NeptuneWSService, NeptuneWSRpc
)

from . test_entity import TestingClientEntity


class Neptune:
    def __init__(self, name):
        self.name = name
        self.init_services()

    def init_services(self):
        np_server = NeptuneServerSkeleton(self.name)
        self.client_manager = NeptuneMessagerManager(TestingClientEntity)

        ws_server = NeptuneWSService('0.0.0.0', '1313')
        wsrpc = NeptuneWSRpc('/13', self.client_manager)
        ws_server.add_route(wsrpc)

        np_server.add_service(wsrpc)
        np_server.add_service(ws_server)
        self.np_server = np_server

    async def run(self):
        await asyncio.gather(
            self.np_server.run(),
        )


if __name__ == '__main__':
    np = Neptune('neptune')
    asyncio.run(np.run())
