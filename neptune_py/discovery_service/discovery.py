from datetime import (timedelta)
import grpc.experimental.aio as agrpc
import neptune_py.proto as proto
from neptune_py.skeleton.grpc_service import (
    NeptuneGRPCService, NeptuneServiceSkeleton
)

from . server_list import ServerList


class DiscoveryService(
        NeptuneGRPCService,
        proto.DiscoveryServicer):

    def __init__(self, ttl=timedelta(seconds=10)):
        super().__init__("DiscoveryService")
        self.server_list = ServerList(ttl)
        self._peers = set()

    def init(self):
        self.server.get_logger().debug("init")

    @property
    def add_to_server(self):
        return lambda x: proto.add_DiscoveryServicer_to_server(
            self, x
        )

    async def Register(self, request, context):
        self.server.get_logger().debug(f"register {request}")
        if not self.server_list.register(request.Id, request):
            return proto.RegisterResponse(
                Error=proto.CommonError(
                    Code=proto.FAILED,
                    Reason=f"pid {request.Id} already exists"
                ),
            )

        return proto.RegisterResponse(
            Error=proto.CommonError(),
            Keepalive=int(self.server_list.ttl.total_seconds())
        )

    async def logic(self):
        self.get_logger().debug("start discovery_service logic")
        while True:
            for context in self._peers:
                await context.write(proto.Servers(
                    Error=proto.CommonError(),
                    Servers=self.server_list.servers
                ))
            await asyncio.sleep(self.server_list.ttl.total_seconds())

    async def Keepalive(self, request_iterator, context):
        pid = None
        try:
            while True:
                request = await context.read()
                self.server.get_logger().debug(f"keepalive request {request}")
                if request == agrpc.EOF:
                    break
                pid = request.Id if pid is None else pid

                if pid != request.Id or (not self.server_list.keepalive(pid)):
                    await context.write(proto.Servers(
                        Error=proto.CommonError(
                            Code=proto.FAILED,
                            Reason="keepalive failed"
                        ),
                    ))
                    break
                self._peers.add(context)
        finally:
            self._peers.discard(context)
            self.server_list.expire_peer(pid)

    async def Echo(self, request, context):
        return request


class DiscoveryServiceClient(NeptuneServiceSkeleton):
    def __init__(self, name, service_info: proto.Server, channel_address):
        super().__init__(name)
        self.channel_address = channel_address
        self.channel = None
        self.stub = None
        self.service_info = service_info
        self.listeners = set()

    def add_listener(self, callback):
        '''
        @param callback: callback function
        '''
        self.listeners.add(callback)

    def remove_listener(self, callback):
        self.listeners.discard(callback)

    def update(self, data):
        for listener in self.listeners:
            listener(data)

    async def keepalive(self, stream, interval):
        while True:
            await stream.write(
                proto.KeepaliveRequest(Id=self.service_info.Id)
            )
            await asyncio.sleep(interval)
        await stream.done_writing()

    async def fetch(self, stream):
        while True:
            response = await stream.read()
            if response == agrpc.EOF:
                break
            self.update(response.Servers)

    async def logic(self):
        self.channel = agrpc.insecure_channel(self.channel_address)
        await self.channel.channel_ready()
        self.stub = proto.DiscoveryStub(self.channel)

        result = await self.stub.Register(self.service_info)

        if result.Error.Code != proto.OK:
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
from neptune_py.stub_service.stub import StubService
import sys


async def test_services():
    np_server = NeptuneServerSkeleton("abc")
    server_info = proto.Server(
        Type="type_any",
        Id=13,
        Address="localhost:1111",
        Services=["Discovery"]
    )

    grpc_server = GRPCServerService("0.0.0.0:1111")
    np_server.add_service(grpc_server)
    np_server.add_service(
        DiscoveryServiceClient("DiscoveryClientService", server_info, "localhost:1313")
    )
    grpc_server.add_service(DiscoveryService())
    np_server.add_service(StubService("DiscoveryClientService"))

    np_server2 = NeptuneServerSkeleton("abc2")
    server_info2 = proto.Server(
        Type="type_any",
        Id=14,
        Address="localhost:2222",
        Services=["Discovery"]
    )

    grpc_server2 = GRPCServerService("0.0.0.0:2222")
    np_server2.add_service(grpc_server2)
    np_server2.add_service(
        DiscoveryServiceClient("DiscoveryClientService", server_info2, "localhost:1313")
    )
    grpc_server2.add_service(DiscoveryService())
    np_server2.add_service(StubService("DiscoveryClientService"))

    await asyncio.gather(
        np_server.run(),
        np_server2.run()
    )

if __name__ == '__main__':
    if sys.argv[1] == 'c':
        asyncio.run(test_services())
        exit(0)

    grpc_service = GRPCServerService("0.0.0.0:1313")
    discovery_service = DiscoveryService()
    np_server = NeptuneServerSkeleton("abc")
    grpc_service.add_service(discovery_service)

    np_server.add_service(grpc_service)
    np_server.add_service(discovery_service)

    asyncio.run(np_server.run())
