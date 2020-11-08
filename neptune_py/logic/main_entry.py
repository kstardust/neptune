import asyncio

from neptune_py.skeleton.skeleton import NeptuneServerSkeleton, NeptuneServiceSkeleton
from neptune_py.skeleton.messager import NeptuneMessagerManager
from neptune_py.skeleton.neptune_rpc.neptune_wsrpc import (
    NeptuneWSService, NeptuneWSRpc
)
from neptune_py.skeleton.neptune_rpc.neptune_tlv import NeptuneTlvService, NeptuneTlvClient
from neptune_py.skeleton.entity import NeptuneEntityBase
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


class EchoEntity(NeptuneEntityBase):
    def on_message(self, message):
        # print(message)
        self.messager.write_message(13, message.message)


class BeepBeepEntity(NeptuneEntityBase):
    def on_connected(self):
        async def beepbeep():
            for i in range(10):
                self.messager.write_message(13, ("hello" + str('13'*i)).encode())
                await asyncio.sleep(1)
            self.messager.close()
        asyncio.create_task(beepbeep())

    def on_message(self, message):
        print(message)


class Neptune:
    def __init__(self, name):
        self.name = name
        self.init_services()

    def init_services(self):
        np_server = NeptuneServerSkeleton(self.name)
        # self.client_manager = NeptuneMessagerManager(TestingClientEntity)
        self.client_manager = NeptuneMessagerManager(EchoEntity)

        # ws_server = NeptuneWSService('0.0.0.0', '1313')
        # wsrpc = NeptuneWSRpc('/13', self.client_manager)
        # ws_server.add_route(wsrpc)
        # ws_server.add_route(WebSocketEcho())

        # np_server.add_service(wsrpc)
        # np_server.add_service(ws_server)
        np_server.add_service(Introspector())
        np_server.add_service(NeptuneTlvService('0.0.0.0', '1313', self.client_manager))

        self.np_server = np_server

        np_server2 = NeptuneServerSkeleton(self.name + "2")
        self.client_manager2 = NeptuneMessagerManager(BeepBeepEntity)
        np_server2.add_service(NeptuneTlvClient('127.0.0.1', '1313', self.client_manager2))

        self.np_server2 = np_server2

    async def run(self):
        async def server2():
            await asyncio.sleep(2)
            await self.np_server2.run()

        await asyncio.gather(
            self.np_server.run(), server2()
        )


if __name__ == '__main__':
    np = Neptune('neptune')
    asyncio.run(np.run())
