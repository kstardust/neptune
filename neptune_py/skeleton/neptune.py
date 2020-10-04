import asyncio

import neptune_py.proto as proto
from neptune_py.skeleton.grpc_service import GRPCServerService
from neptune_py.skeleton.skeleton import NeptuneServerSkeleton
from neptune_py.skeleton.messager import NeptuneMessagerManager, NeptuneMessageType
from neptune_py.skeleton.entity import NeptuneEntityBase
from neptune_py.skeleton.neptune_rpc.neptune_wsrpc import (
    NeptuneWSService, NeptuneWSRpc
)

from neptune_py.skeleton.neptune_rpc.neptune_grpcrpc import (
    NeptuneGRPCRPCService, NeptuneGRPCRPCClient
)


class TestEntity(NeptuneEntityBase):
    def RpcReqCallServer(self, arg):
        print(f'RpcReqTestEcho, {arg}')
        # self.RpcStub.RpcResponseTestEcho(arg)
        self.RpcStub.NestedCall1('13').FinalCall(13)


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
        elif test_flag == 's':
            manager = NeptuneMessagerManager(TestEntity)
            grpc_server = GRPCServerService("0.0.0.0:1313")
            grpc_server.add_service(NeptuneGRPCRPCService(manager))

            ws_server = NeptuneWSService('0.0.0.0', '1314')
            wsrpc = NeptuneWSRpc('/echo', manager)
            ws_server.add_route(wsrpc)

            np_server.add_service(wsrpc)

            np_server.add_service(ws_server)
            np_server.add_service(grpc_server)

        await asyncio.gather(
            np_server.run(),
        )


if __name__ == '__main__':
    import sys
    asyncio.run(Neptune('neptune').run(sys.argv[1]))
