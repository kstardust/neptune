
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
        subnet += ':'

        if subnet != self.local_addr:
            self.get_logger().error("should forward, not yet implmented {} {}".format(subnet, self.local_addr))
            return

        for peer in self.m_setPeers:
            if peer.PeerAddr == dest:
                peer.send_message(NeptuneMessageType.NeptuneMessageTypeForward, message)
                return
        # forward to router


class NeptuneRouter:
    def __init__(self, name):
        self.name = name
        self.init_services()

    def init_services(self):
        np_server = NeptuneServerSkeleton(self.name)
        np_server.profile = {
            "addr4router": ('127.0.0.1', '1315'),
            "local_addr": "13:"
        }
        # self.client_manager = NeptuneMessagerManager(TestingClientEntity)
        self.port_manager = NeptuneMessagerManager(NeptuneRouterPort)
        self.router_port_manager = NeptuneMessagerManager(NeptuneRouterRouterPort)

        np_server.add_service(RouterEntityManager("RouterEntityManager"))
        np_server.add_service(Introspector())
        np_server.add_service(NeptuneTlvClient('0.0.0.0', '1313', NeptuneMessagerManager(NeptuneRouterManagerInRouter)))
        np_server.add_service(NeptuneTlvService('0.0.0.0', '1316', self.port_manager))
        np_server.add_service(NeptuneTlvService('0.0.0.0', '1315', self.router_port_manager))

        self.np_server = np_server

    async def run(self):
        async def server2():
            await asyncio.sleep(2)
            await self.np_server2.run()

        await asyncio.gather(
            self.np_server.run()
        )
