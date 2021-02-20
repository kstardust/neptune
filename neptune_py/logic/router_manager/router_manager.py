import asyncio

from neptune_py.skeleton.skeleton import NeptuneServerSkeleton, NeptuneServiceSkeleton
from neptune_py.skeleton.messager import NeptuneMessagerManager
from neptune_py.skeleton.transporter.neptune_tlv import NeptuneTlvService, NeptuneTlvClient
from neptune_py.skeleton.entity.entity import NeptuneEntityBase
from neptune_py.skeleton.introspector import Introspector
from . router import NeptuneRouterInRouterManager
from neptune_py.etc.config import get_profile


class RouterEntityManager(NeptuneServiceSkeleton):
    def __init__(self, name):
        super().__init__(name)
        self.m_setRouters = set()

    def RegisterRouter(self, Router):
        self.m_setRouters.add(Router)
        self.get_logger().info("RegisterRouter", Router.RouterInfo)
        for Router in self.m_setRouters:
            Router.rpc_stub.RouterConnectTo(Router.RouterInfo)

    def UnRegisterRouter(self, Router):
        self.m_setRouters.discard(Router)
        self.get_logger().info("UnRegisterRouter", Router.RouterInfo)


class NeptuneRouterManagerApp:
    def __init__(self, name):
        self.name = name
        self.init_services()

    def init_services(self):
        np_server = NeptuneServerSkeleton(self.name)
        self.client_manager = NeptuneMessagerManager(NeptuneRouterInRouterManager)

        np_server.add_service(RouterEntityManager("RouterEntityManager"))
        np_server.add_service(Introspector())

        addr4router = np_server.profile.get('addr4router')
        np_server.add_service(NeptuneTlvService(*addr4router, self.client_manager))

        self.np_server = np_server

    async def run(self):
        await asyncio.gather(
            self.np_server.run()
        )
