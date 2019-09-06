import asyncio
import setting
import argparse
import sys

parser = argparse.ArgumentParser(description="neptune")
parser.add_argument('-c', help='client mode', action='store_true')


async def se_server_handler(cls, reader, writer):
    peer = cls(reader, writer, bk_size=setting.BLOCK_SIZE)
    await peer.serve()


async def se_client_handler(cls, reader, writer):
    peer = cls(reader, writer)
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
    data = sys.stdin.readline()
    asyncio.create_task(peer.send(data.encode('utf8')))


async def client():
    reader, writer = await asyncio.open_connection(
        setting.ADDR, setting.PORT
    )

    await se_client_handler(setting.PEER_CLASS, reader, writer)


from proto.neptune_rpc import main

if __name__ == '__main__':
    main()
    exit(0)
    args = parser.parse_args()
    if args.c:
        asyncio.run(client())
    else:
        asyncio.run(server())
