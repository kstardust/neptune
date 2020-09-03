from datetime import (timedelta)
import weakref
import grpc.experimental.aio as agrpc
from neptune_py.proto import discovery_service_pb2
from neptune_py.proto import discovery_service_pb2_grpc
from neptune_py.proto import error_pb2
from neptune_py.skeleton.grpc_service import (
    NeptuneGRPCService, NeptuneServiceSkeleton
)

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


class DiscoveryServiceClient(NeptuneServiceSkeleton):
    def __init__(self, name, channel_address):
        super().__init__(name)
        self.channel_address = channel_address
        self.channel = None
        self.stub = None
        self.listeners = weakref.WeakSet()

    def add_listener(self, callback):
        '''
        @param callback: callback function
        '''
        self.listeners.add(callback)

    def update(self):
        for listener in self.listeners:
            listener(self)

    async def keepalive(self, stream, interval):
        while True:
            await stream.write(
                discovery_service_pb2.KeepaliveRequest(Id=13)
            )
            await asyncio.sleep(interval)
        await stream.done_writing()

    async def fetch(self, stream, interval):
        while True:
            response = await stream.read()
            if response == agrpc.EOF:
                break
            print(response)
            self.update()

    async def logic(self):
        self.channel = agrpc.insecure_channel(self.channel_address)
        await self.channel.channel_ready()
        self.stub = discovery_service_pb2_grpc.DiscoveryStub(self.channel)

        request = discovery_service_pb2.Server(Type="type_any", Id=13)
        result = await self.stub.Echo("hello")
        print(result)

        result = await self.stub.Register(request)
        print(result.Error.Code, result.Keepalive)

        stream = self.stub.Keepalive()
        await asyncio.gather(
            self.keepalive(stream, 1),
            self.fetch(stream)
        )

    async def finish(self):
        if self.channel is not None:
            await self.channel.close()


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
