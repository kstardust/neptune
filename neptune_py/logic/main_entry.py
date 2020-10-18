import asyncio

from neptune_py.skeleton.skeleton import NeptuneServerSkeleton, NeptuneServiceSkeleton
from neptune_py.skeleton.messager import NeptuneMessagerManager
from neptune_py.skeleton.neptune_rpc.neptune_wsrpc import (
    NeptuneWSService, NeptuneWSRpc
)

from . test_entity import TestingClientEntity


class Introspector(NeptuneServiceSkeleton):
    def __init__(self):
        super().__init__('Introspector')

    async def logic(self):
        while True:
            self.get_logger().debug(f'current tasks(coroutines) {len(asyncio.all_tasks())}')
            await asyncio.sleep(5)


from aiohttp import web
import aiohttp


class WebSocketEcho:
    def __init__(self):
        self._route = "/echo"

    def route(self):
        return (self._route, self.websocket_handler)

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT or msg.type == aiohttp.WSMsgType.BINARY:
                print(f"received: {msg.data}")
                await ws.send_str(msg.data)
            else:
                self.get_logger().debug(f'unexpected type {msg.typ}')
                break


class Neptune:
    def __init__(self, name):
        self.name = name
        self.init_services()

    def init_services(self):
        np_server = NeptuneServerSkeleton(self.name)
        self.client_manager = NeptuneMessagerManager(TestingClientEntity)

        ws_server = NeptuneWSService('0.0.0.0', '1313')
        wsrpc = NeptuneWSRpc('/13', self.client_manager)
        ws_server.add_route(wsrpc)
        ws_server.add_route(WebSocketEcho())

        np_server.add_service(wsrpc)
        np_server.add_service(ws_server)
        np_server.add_service(Introspector())
        self.np_server = np_server

    async def run(self):
        await asyncio.gather(
            self.np_server.run(),
        )


if __name__ == '__main__':
    np = Neptune('neptune')
    asyncio.run(np.run())
