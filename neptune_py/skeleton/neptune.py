import asyncio

import neptune_py.proto as proto
from neptune_py.skeleton.grpc_service import GRPCServerService
from neptune_py.skeleton.skeleton import NeptuneServerSkeleton
from neptune_py.skeleton.messager import NeptuneMessagerManager, NeptuneMessageType
from neptune_py.skeleton.entity import NeptuneEntityBase

from neptune_py.skeleton.neptune_rpc.neptune_rpc import (
    NeptuneGRPCRPCService, NeptuneGRPCRPCClient
)


class TestEntity(NeptuneEntityBase):
    def RpcReqTestEcho(self, arg):
        print(f'RpcReqTestEcho, {arg}')
        self.RpcStub.RpcResponseTestEcho(arg)


class TestClientEntity(NeptuneEntityBase):
    def RpcResponseTestEcho(self, arg):
        print(f'RpcResponseTestEcho, {arg}')

    def on_connected(self):
        self.RpcStub.RpcReqTestEcho('hands across the sea')


class Neptune:
    def __init__(self, name):
        self.init_services()

    def init_services(self):
        pass

    async def run(self, test_flag):
        np_server = NeptuneServerSkeleton("abc")

        if test_flag == 'c':
            client_manager = NeptuneMessagerManager(TestClientEntity)
            np_server.add_service(NeptuneGRPCRPCClient(client_manager, "127.0.0.1:1313"))
        else:
            manager = NeptuneMessagerManager(TestEntity)
            grpc_server = GRPCServerService("0.0.0.0:1313")
            np_server.add_service(grpc_server)
            grpc_server.add_service(NeptuneGRPCRPCService(manager))

        await asyncio.gather(
            np_server.run(),
        )


if __name__ == '__main__':
    import sys
    asyncio.run(Neptune('neptune').run(sys.argv[1]))
