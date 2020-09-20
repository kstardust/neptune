import asyncio
import neptune_py.proto as proto
from neptune_py.skeleton.grpc_service import (
    NeptuneGRPCService, NeptuneServiceSkeleton
)


class NeptuneRPCServiceImp(proto.NeptuneRPCServicer):
    def __init__(self, service):
        self.service = service

    async def MessageStream(self, request, context):
        messager = await self.service.MessageStreamStart(context)
        try:
            while True:
                message = await context.read()
                await self.service.MessageArrived(messager, message)
        finally:
            await self.service.MessageStreamEnd(messager)

        print("start rpc stream")


class NeptuneMessagerBase:
    # TODO: encapslate grpc_ctx into a general ReadWriter
    def __init__(self, grpc_ctx):
        self.grpc_ctx = grpc_ctx

    def Send(self, message):
        asyncio.create_task(self.grpc_ctx.write(message))

    async def SyncSend(self, message):
        await self.grpc_ctx.write(message)

    async def Start(self):
        print("message stream start")

    async def End(self):
        print("message stream end")

    async def Message(self, message):
        print(message)


class NeptuneRPCService(NeptuneGRPCService):
    def __init__(self, entity_class, name=None):
        super().__init__(name)
        self.entity_class = entity_class
        self._grpc_imp = NeptuneRPCServiceImp(self)
        self._messagers = {}

    @property
    def add_to_server(self):
        return lambda x: proto.add_DiscoveryServicer_to_server(
            self._grpc_imp, x
        )

    def init(self):
        self.server.get_logger().debug(f"start neptune rpc service {self.name}")

    async def logic(self):
        self.get_logger().debug(f"start neptune rpc logic {self.name}")

    async def MessageStreamStart(self, grpc_ctx):
        messager = self.entity_class(grpc_ctx)
        await messager.Start()

    async def MessageStreamEnd(self, messager):
        self._messagers.pop(messager)
        await messager.End()

    async def MessageArrived(self, messager, message):
        print(message)
        await messager.Message(message)


class TestNMsgServiceClient(NeptuneServiceSkeleton):
    def __init__(self, name, service_info: proto.Server, channel_address):
        super().__init__(name)
        self.channel_address = channel_address
        self.channel = None
        self.stub = None
        self.service_info = service_info
        self.listeners = set()

    async def write(self, stream):
        while True:
            await stream.write(
                proto.NeptuneMessage(
                    MsgType=proto.NeptuneMessageTypeCall,
                    Payload="helloworld13"
                )
            )
            await asyncio.sleep(1)
        await stream.done_writing()

    async def read(self, stream):
        while True:
            message = await stream.read()
            if message == agrpc.EOF:
                break
            print(message)

    async def logic(self):
        self.channel = agrpc.insecure_channel(self.channel_address)
        await self.channel.channel_ready()
        self.stub = proto.NeptuneMessageStreamStub()

        stream = self.stub.Keepalive()
        await asyncio.gather(
            self.read(stream),
            self.write(stream),
            return_exceptions=True
        )

    async def finish(self):
        if self.channel is not None:
            await self.channel.close()


import sys
import grpc.experimental.aio as agrpc
from neptune_py.skeleton.grpc_service import (
    GRPCServerService, NeptuneServerSkeleton
)


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
        
