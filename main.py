import asyncio
import setting
import argparse
import sys
import random
from service.foo import FooService, FooRequest, Foo_Stub
from service.bar import BarService, BarRequest, Bar_Stub

foo = FooService()
bar = BarService()

parser = argparse.ArgumentParser(description="neptune")
parser.add_argument('-c', help='client mode', action='store_true')


async def se_server_handler(cls, reader, writer):
    peer = cls(reader, writer, bk_size=setting.BLOCK_SIZE, services=[foo, bar])
    await peer.serve()


async def se_client_handler(cls, reader, writer):
    peer = cls(reader, writer, services=[foo, bar])
    loop = asyncio.get_event_loop()
    loop.add_reader(sys.stdin, lambda: input_reader(peer))
    await peer.serve()


async def server():
    server = await asyncio.start_server(
        lambda r, w: se_server_handler(setting.PEER_CLASS, r, w),
        setting.ADDR, setting.PORT
    )
    async with server:
        await server.serve_forever()


def input_reader(peer):
    foo_stub = Foo_Stub(peer.rpc_channel)
    bar_stub = Bar_Stub(peer.rpc_channel)
    data = sys.stdin.readline()
    req = FooRequest()
    req.message = "test"
    if random.randrange(0, 2) == 1:
        asyncio.create_task(foo_stub.Foo(None, req, lambda x: print(x)))
    else:
        asyncio.create_task(bar_stub.Bar(None, req, lambda x: print(x)))


async def client():
    reader, writer = await asyncio.open_connection(
        setting.ADDR, setting.PORT
    )

    await se_client_handler(setting.PEER_CLASS, reader, writer)


TEST = True
from proto.neptune_rpc import main

if __name__ == '__main__':
    args = parser.parse_args()
    if args.c:
        asyncio.run(client())
    else:
        asyncio.run(server())
