import asyncio
import traceback
from neptune_py.skeleton.skeleton import NeptuneServiceSkeleton
from neptune_py.skeleton.messager import (
    NeptuneWriterBaseAbstract, NeptuneMessageType
)

import struct
import collections


class TLV:
    _format = '!HI'
    meta_size = struct.calcsize(_format)
    tlv = collections.namedtuple('tlv_tuple', 'tag length')
    MagicTag = 13

    @classmethod
    def pack(cls, tag, data):
        return struct.pack(cls._format, tag, len(data)) + data

    @classmethod
    def unpack(cls, data):
        if len(data) < cls.meta_size:
            return None
        tag, length = struct.unpack(cls._format, data)
        return cls.tlv(tag=tag, length=length)


class TlvWriter(NeptuneWriterBaseAbstract):
    def __init__(self, writer):
        super().__init__()
        self.writer = writer
        self.closed = False

    def write(self, message):
        self.writer.write(TLV.pack(TLV.MagicTag, message))

    def close(self):
        if self.closed:
            return
        self.closed = True

        if self.writer.can_write_eof():
            self.writer.write_eof()
        else:
            self.writer.close()


class NeptuneTlvBase(NeptuneServiceSkeleton):

    def __init__(self, host, port, messager_manager, name=None):
        super().__init__(name)
        self.host = host
        self.port = port
        self.messager_manager = messager_manager
        self.messager_id = 0

    async def connection_handler(self, reader, writer):
        peername = writer.get_extra_info("peername")
        self.get_logger().debug(f'{peername} connected')

        messager_id = self.messager_id
        tlv_writer = TlvWriter(writer)
        self.messager_manager.on_connected(messager_id, tlv_writer)
        self.messager_id += 1

        try:
            while True:
                meta = await reader.readexactly(TLV.meta_size)
                tlv = TLV.unpack(meta)
                # print(tlv)
                data = await reader.readexactly(tlv.length)
                self.messager_manager.on_message(messager_id, data)
        except asyncio.IncompleteReadError as e:
            if e.partial:
                # empty data indicates peer closed the connection, otherwise the data
                # is illegal.
                self.get_logger().debug(f'{peername} illegal data')
        except Exception as e:
            self.get_logger().error(traceback.format_exc())
        finally:
            self.get_logger().debug(f'{peername} closed')
            self.messager_manager.on_disconnected(messager_id)
            writer.close()
            await writer.wait_closed()

    def init(self):
        self.get_logger().debug(f'init {self.__class__.__name__} {self.name}')

    async def finish(self):
        self.get_logger().debug(f'stopping {self.__class__.__name__} {self.name}...')


class NeptuneTlvService(NeptuneTlvBase):
    """
    tlv message server
    """
    async def logic(self):
        # https://docs.python.org/3.6/library/asyncio-protocol.html
        # 'Changed in version 3.6: The socket option TCP_NODELAY is now set by default.'
        server = await asyncio.start_server(self.connection_handler, self.host, self.port)
        async with server:
            self.get_logger().debug(f'NeptuneTlvService {self.name} starts to server')
            await server.serve_forever()


class NeptuneTlvClient(NeptuneTlvBase):
    """
    tlv message client
    """
    async def logic(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        await self.connection_handler(reader, writer)
