import asyncio
from aiohttp import web
import aiohttp

from neptune_py.skeleton.skeleton import NeptuneServiceSkeleton
from neptune_py.skeleton.messager import (
    NeptuneWriterBaseAbstract, NeptuneMessageTuple, NeptuneMessageType
)


class NeptuneWSServiceError(Exception):
    pass


class NeptuneWSServiceAmbiguousRoute(NeptuneWSServiceError):
    pass


class NeptuneWSRouteMixin:
    def route(self):
        """
        return: a tuple: (route_path, handler)
        """
        raise NotImplemented('please implement this method')


class NeptuneWSService(NeptuneServiceSkeleton):

    def __init__(self, host, port, name=None):
        super().__init__(name)
        self.host = host
        self.port = port
        self.runner = None
        self.routes = {}

    def init(self):
        self.ws_app = web.Application()
        for route, handler in self.routes.items():
            self.ws_app.add_routes([web.get(route, handler)])
            self.get_logger().debug(f'add route {route}')
        self.get_logger().debug(f'init NeptuneWSService {self.name}')

    async def logic(self):
        # https://docs.aiohttp.org/en/stable/web_advanced.html#application-runners
        self.runner = web.AppRunner(self.ws_app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.host, self.port)
        self.get_logger().debug(f'start logic NeptuneWSService {self.name}')
        await site.start()

    async def stop(self):
        self.get_logger().debug(f'stopping NeptuneWSService {self.name}...')
        if self.runner:
            await self.runner.cleanup()

    def add_route(self, ws_route: NeptuneWSRouteMixin):
        r, h = ws_route.route()
        if r in self.routes:
            raise NeptuneWSServiceAmbiguousRoute()
        self.routes[r] = h


class NeptuneWSRpcWriter(NeptuneWriterBaseAbstract):
    def __init__(self, ws):
        self.ws = ws

    def write(self, message_type: NeptuneMessageType, message):
        asyncio.create_task(self.ws.send_str('{:02d}{}'.format(message_type, message)))

    def close(self):
        asyncio.create_task(self.ws.close())


class NeptuneWSRpc(NeptuneServiceSkeleton, NeptuneWSRouteMixin):
    def __init__(self, route, messager_manager, name='NeptuneWSRpc'):
        super().__init__(name)
        self._route = route
        self.messager_manager = messager_manager
        self.messager_id = 0

    def route(self):
        return (self._route, self.websocket_handler)

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.messager_id += 1
        messager_id = self.messager_id

        self.messager_manager.on_connected(messager_id, NeptuneWSRpcWriter(ws))

        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT or msg.type == aiohttp.WSMsgType.BINARY:
                    mtype, mpayload = int(msg.data[:2]), msg.data[2:]
                    np_message = NeptuneMessageTuple(
                        type=mtype,
                        message=mpayload
                    )
                    self.messager_manager.on_message(messager_id, np_message)
                else:
                    self.get_logger().debug(f'unexpected type {msg.typ}')
                    break
        finally:
            # async for ws will raise execeptions when ws is closed abnormally
            self.get_logger().debug(f'ws closed')
            await ws.close()
            self.messager_manager.on_disconnected(self.messager_id)

        return ws


class NeptuneWSRpcClient(NeptuneServiceSkeleton):
    def __init__(self, address):
        raise NotImplementedError('server side doest support websocket client, alse it\'s not necessary.')
