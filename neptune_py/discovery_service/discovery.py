from datetime import (timedelta)
from neptune_py.proto import discovery_service_pb2
from neptune_py.proto import discovery_service_pb2_grpc
from neptune_py.proto import error_pb2
from neptune_py.skeleton.grpc_service import NeptuneGRPCService


from . server_list import ServerList


class DiscoveryService(
        NeptuneGRPCService,
        discovery_service_pb2_grpc.DiscoveryServicer):

    def __init__(self, ttl=timedelta(seconds=10)):
        super().__init__("DiscoveryService")
        self.server_list = ServerList(ttl)
        self._peers = {}

    def init(self):
        self.server.get_logger().debug("init")

    @property
    def add_to_server(self):
        return lambda x: discovery_service_pb2_grpc.add_DiscoveryServicer_to_server(
            self, x
        )

    async def Register(self, request, context):
        print("Register", request)
        if not self.server_list.register(request.Id, request):
            return discovery_service_pb2.RegisterResponse(
                Error=error_pb2.CommonError(
                    Code=error_pb2.FAILED,
                    Reason=f"pid {request.Id} already exists"
                ),
            )
        return discovery_service_pb2.RegisterResponse(
            Error=error_pb2.CommonError(),
            Keepalive=int(self.server_list.ttl.total_seconds())
        )

    async def _keepalive_reader(self, request_iterator):
        async for request in request_iterator:
            print(request)
            self.server_list.keepalive(request.Id)

    async def Keepalive(self, request_iterator, context):
        print("keepalive start")
        # input_ = asyncio.create_task(self._keepalive_reader(request_iterator))
        # while True:
        #     yield discovery_service_pb2.Servers(
        #         Error=error_pb2.CommonError(),
        #         Servers=self.server_list.servers
        #     )
        #     await asyncio.sleep(self.server_list.ttl.total_seconds())
        # # await context.abort(grpc.StatusCode.CANCELLED)
        # await input_

    async def Echo(self, request, context):
        return request

import asyncio
from neptune_py.skeleton.grpc_service import GRPCServerService
from neptune_py.skeleton.skeleton import NeptuneServerSkeleton


if __name__ == '__main__':
    grpc_service = GRPCServerService("0.0.0.0:1313")
    discovery_service = DiscoveryService()
    np_server = NeptuneServerSkeleton("abc")
    grpc_service.add_service(discovery_service)

    np_server.add_service(grpc_service)
    np_server.add_service(discovery_service)
    asyncio.run(np_server.run())
