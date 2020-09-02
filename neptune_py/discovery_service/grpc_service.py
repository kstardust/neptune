import grpc.experimental.aio as agrpc
from datetime import (datetime, timedelta)
from neptune_py.proto import discovery_service_pb2
from neptune_py.proto import error_pb2
from neptune_py.proto import discovery_service_pb2_grpc

from . skeleton import NeptuneServiceSkeleton


class NeptuneGRPCService(NeptuneServiceSkeleton):
    def add_to_server(self):
        raise NotImplementedError()


class GRPCServerService(NeptuneServiceSkeleton):
    def __init__(self, bind_address):
        super().__init__("grpc")
        self.bind_address = bind_address

    def init(self):
        self.server = agrpc.server()
        self.server.add_insecure_port(self.bind_address)

    async def logic(self):
        await self.server.start()
        await self.server.wait_for_termination()

    def add_service(self, grpc_service: NeptuneGRPCService):
        grpc_service.add_to_server(self)


class DiscoveryService(
        NeptuneGRPCService,
        discovery_service_pb2_grpc.DiscoveryServicer):

    def __init__(self, ttl=timedelta(seconds=10)):
        super().__init__("DiscoveryService")
        self.server_list = None #ServerList(ttl)
        self._peers = {}

    def init(self):
        self.server.get_logger().debug("init")

    @property
    def add_to_server(self):
        return lambda x: discovery_service_pb2.add_DiscoveryServicer_to_server(
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
        input_ = asyncio.create_task(self._keepalive_reader(request_iterator))
        while True:
            yield discovery_service_pb2.Servers(
                Error=error_pb2.CommonError(),
                Servers=self.server_list.servers
            )
            await asyncio.sleep(self.server_list.ttl.total_seconds())
        # await context.abort(grpc.StatusCode.CANCELLED)
        await input_
