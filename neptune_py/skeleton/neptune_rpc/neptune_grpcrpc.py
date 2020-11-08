import asyncio
import neptune_py.proto as proto
import grpc.experimental.aio as agrpc
import traceback
from neptune_py.skeleton.grpc_service import NeptuneGRPCService
from neptune_py.skeleton.skeleton import NeptuneServiceSkeleton
from neptune_py.skeleton.messager import (
    NeptuneMessagerManager, NeptuneWriterBaseAbstract, NeptuneMessageTuple
)


class NeptuneRPCServiceImp(proto.NeptuneMessageStream):
    def __init__(self, service):
        self.service = service
        self._stream_id = 0

    async def MessageStream(self, request, context):
        self._stream_id += 1
        stream_id = self._stream_id
        await self.service.MessageStreamStart(stream_id, context)
        try:
            while True:
                message = await context.read()
                if message == agrpc.EOF:
                    break

                mtype = message.MsgType,
                payload = message.Payload

                await self.service.MessageArrived(stream_id, payload)
        finally:
            await self.service.MessageStreamEnd(stream_id)


class NeptuneGRPCRPCWriter(NeptuneWriterBaseAbstract):
    def __init__(self, grpc_ctx):
        self.raw_stream = grpc_ctx

    def write(self, message):
        asyncio.create_task(self.raw_stream.write(
            proto.NeptuneMessage(
                MsgType=13,
                Payload=message
            )
        ))

    def close(self):
        pass


class NeptuneGRPCRPCService(NeptuneGRPCService):
    '''
    neptune rpc by grpc
    '''
    def __init__(self, messager_manager: NeptuneMessagerManager, name=None):
        super().__init__(name)
        self.messager_manager = messager_manager
        self._grpc_imp = NeptuneRPCServiceImp(self)

    @property
    def add_to_server(self):
        return lambda x: proto.add_NeptuneMessageStreamServicer_to_server(
            self._grpc_imp, x
        )

    def init(self):
        self.server.get_logger().debug(f"start neptune rpc service {self.name}")

    async def logic(self):
        self.get_logger().debug(f"start neptune rpc logic {self.name}")

    async def MessageStreamStart(self, stream_id, grpc_ctx):
        self.messager_manager.on_connected(stream_id, NeptuneGRPCRPCWriter(grpc_ctx))

    async def MessageStreamEnd(self, stream_id):
        self.messager_manager.on_disconnected(stream_id)

    async def MessageArrived(self, stream_id, message):
        print(f'message arrived: {stream_id}, {message}')
        self.messager_manager.on_message(stream_id, message)


class NeptuneGRPCRPCClient(NeptuneServiceSkeleton):
    def __init__(self, message_manager, channel_address, name=None):
        super().__init__(name)
        self.channel_address = channel_address
        self.message_manager = message_manager
        self.channel = None
        self.stub = None

    async def read_stream(self, stream_id, stream):
        try:
            while True:
                message = await stream.read()
                if message == agrpc.EOF:
                    break

                type = message.MsgType,
                payload = message.Payload

                print('read stream recv message:', payload)
                self.message_manager.on_message(stream_id, payload)
        except Exception as e:
            self.get_logger().error('grpc stream read error {}'.format(traceback.format_exc()))
        finally:
            self.message_manager.on_disconnected(1)

    async def logic(self):
        self.get_logger().debug(f'start run service logic: {self.name}')
        self.channel = agrpc.insecure_channel(self.channel_address)
        await self.channel.channel_ready()

        self.stub = proto.NeptuneMessageStreamStub(self.channel)
        stream = self.stub.MessageStream()

        # client is an unique stream, it's not necessary to offer an id
        self.message_manager.on_connected(1, NeptuneGRPCRPCWriter(stream))

        await self.read_stream(1, stream)

    async def finish(self):
        if self.channel is not None:
            await self.channel.close()
