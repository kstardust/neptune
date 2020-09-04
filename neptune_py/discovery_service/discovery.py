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
        self._peers = set()

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

    async def logic(self):
        self.get_logger().debug("start discovery_service logic")
        while True:
            for context in self._peers:
                await context.write(discovery_service_pb2.Servers(
                    Error=error_pb2.CommonError(),
                    Servers=self.server_list.servers
                ))
            await asyncio.sleep(self.server_list.ttl.total_seconds())

    async def Keepalive(self, request_iterator, context):
        print("keepalive start")
        pid = None
        try:
            while True:
                request = await context.read()
                print(f"request {request}")
                if request == agrpc.EOF:
                    break
                pid = request.Id if pid is None else pid

                if pid != request.Id or (not self.server_list.keepalive(pid)):
                    await context.write(discovery_service_pb2.Servers(
                        Error=error_pb2.CommonError(
                            Code=error_pb2.FAILED,
                            Reason="keepalive failed"
                        ),
                    ))
                    break
                self._peers.add(context)
        finally:
            self._peers.discard(context)
            self.server_list.expire_peer(pid)


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
            print("---------keepalive request")
            await stream.write(
                discovery_service_pb2.KeepaliveRequest(Id=13)
            )
            await asyncio.sleep(interval)
        await stream.done_writing()

    async def fetch(self, stream):
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
        result = await self.stub.Register(request)
        print(result.Error, result.Keepalive)

        if result.Error.Code != error_pb2.OK:
            return

        stream = self.stub.Keepalive()
        await asyncio.gather(
            self.keepalive(stream, result.Keepalive * 0.8),
            self.fetch(stream),
            return_exceptions=True
        )

    async def finish(self):
        if self.channel is not None:
            await self.channel.close()


import asyncio
from neptune_py.skeleton.grpc_service import GRPCServerService
from neptune_py.skeleton.skeleton import NeptuneServerSkeleton
import sys

if __name__ == '__main__':
    if sys.argv[1] == 'c':
        np_server = NeptuneServerSkeleton("abc")
        np_server.add_service(DiscoveryServiceClient("dservice", "localhost:1313"))
        asyncio.run(np_server.run())
        exit(0)

    grpc_service = GRPCServerService("0.0.0.0:1313")
    discovery_service = DiscoveryService()
    np_server = NeptuneServerSkeleton("abc")
    grpc_service.add_service(discovery_service)

    np_server.add_service(grpc_service)
    np_server.add_service(discovery_service)
    asyncio.run(np_server.run())
