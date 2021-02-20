
import asyncio

import neptune_py.skeleton.skeleton as sk
from neptune_py.skeleton.skeleton import NeptuneServerSkeleton, NeptuneServiceSkeleton
from neptune_py.skeleton.messager import NeptuneMessagerManager
from neptune_py.skeleton.transporter.neptune_tlv import NeptuneTlvService, NeptuneTlvClient
from neptune_py.skeleton.entity.entity import NeptuneEntityBase
from neptune_py.skeleton.introspector import Introspector
from neptune_py.skeleton.neptune_rpc.decorator import rpc
from neptune_py.skeleton.messager import NeptuneMessageType
from .router_port import NeptuneRouterPort, NeptuneRouterRouterPort
from neptune_py.etc.config import get_profile


class NeptuneRouterManagerInRouter(NeptuneEntityBase):
    def __init__(self, entity_id, rpc_exec=True):
        super().__init__(entity_id, rpc_exec)
        self.set_local_addr(sk.G.profile.get('local_addr'))

    def on_connected(self):
        self.rpc_stub.RegisterRouter(sk.G.profile)

    async def ConnectToRouter(self, address):
        service = NeptuneTlvClient(*address, NeptuneMessagerManager(NeptuneRouterRouterPort))
        service.init_service(sk.G)
        await service.run()

    @rpc()
    def RouterConnectTo(self, dictRouterInfo):
        self.logger.info("RouterConnectTo {}".format(dictRouterInfo))
        asyncio.create_task(self.ConnectToRouter(dictRouterInfo["addr4router"]))


class RouterEntityManager(NeptuneServiceSkeleton):
    def __init__(self, name):
        super().__init__(name)
        self.m_setRouters = set()
        self.m_setPeers = set()
        self.local_addr = sk.G.profile.get('local_addr')

    def RegisterRouterInRouter(self, Router):
        self.m_setRouters.add(Router)
        self.get_logger().info("RegisterRouterInRouter", Router.PeerInfo)

    def UnRegisterRouterInRouter(self, Router):
        self.m_setRouters.discard(Router)
        self.get_logger().info("UnRegisterRouter", Router.PeerInfo)

    def RegisterPeerInRouter(self, Peer):
        self.m_setPeers.add(Peer)
        self.get_logger().info("Register Peer", Peer.PeerInfo)

    def UnRegisterPeerInRouter(self, Peer):
        self.m_setPeers.discard(Peer)
        self.get_logger().info("UnRegister Peer", Peer.PeerInfo)

    def Forward(self, dest, message):
        # forward to dest
        subnet, _ = dest.split(':', maxsplit=1)
        subnet += '::'

        if subnet != self.local_addr:
            self.get_logger().error("should forward, not yet implmented {} {}".format(subnet, self.local_addr))
            return

        serverDest, _ = dest.rsplit(':', maxsplit=1)
        serverDest += ':'

        for peer in self.m_setPeers:
            if peer.PeerAddr == serverDest:
                peer.send_message(NeptuneMessageType.NeptuneMessageTypeForward, message)
                return
        # forward to router

        self.get_logger().error("unknown destination: {}".format(dest))


class NeptuneRouter:
    def __init__(self, name):
        self.name = name
        self.init_services()

    def init_services(self):
        np_server = NeptuneServerSkeleton(self.name)
        # self.client_manager = NeptuneMessagerManager(TestingClientEntity)
        self.port_manager = NeptuneMessagerManager(NeptuneRouterPort)
        self.router_port_manager = NeptuneMessagerManager(NeptuneRouterRouterPort)

        np_server.add_service(RouterEntityManager("RouterEntityManager"))
        np_server.add_service(Introspector())
        router_manager_addr = get_profile('router_manager').get('addr4router')
        np_server.add_service(NeptuneTlvClient(*router_manager_addr, NeptuneMessagerManager(NeptuneRouterManagerInRouter)))
        np_server.add_service(NeptuneTlvService(
            *np_server.profile.get('addr4port'),
            self.port_manager)
        )
        np_server.add_service(NeptuneTlvService(
            *np_server.profile.get('addr4router'),
            self.router_port_manager)
        )

        self.np_server = np_server

    async def run(self):
        await asyncio.gather(
            self.np_server.run()
        )
