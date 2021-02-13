from neptune_py.skeleton.entity.entity import NeptuneEntityBase
import neptune_py.skeleton.skeleton as sk
from neptune_py.skeleton.neptune_rpc.decorator import rpc


class NeptuneRouterRouterPort(NeptuneEntityBase):
    def __init__(self, entity_id, rpc_exec=True):
        super().__init__(entity_id, rpc_exec)
        self.m_dictPeerInfo = {}
        self.m_RouterManager = sk.G.find_service("RouterEntityManager")
        assert self.m_RouterManager is not None

    @property
    def PeerInfo(self):
        return self.m_dictPeerInfo

    @property
    def PeerAddr(self):
        return self.m_dictPeerInfo.get('local_addr')

    def on_connected(self):
        print("=========================")
        self.rpc_stub.RegisterRouterInRouter(sk.G.profile)

    def on_messager_lost(self, messager):
        super().on_messager_lost(messager)
        self.m_RouterManager.UnRegisterRouterInRouter(self)

    @rpc()
    def RegisterRouterInRouter(self, dictRouterInfo):
        print("RegisterRouterInRouter=========================", dictRouterInfo)
        self.m_dictPeerInfo = dictRouterInfo
        self.m_RouterManager.RegisterRouterInRouter(self)


class NeptuneRouterPort(NeptuneEntityBase):
    def __init__(self, entity_id, rpc_exec=True):
        super().__init__(entity_id, rpc_exec)
        self.m_dictPeerInfo = {}
        self.m_RouterManager = sk.G.find_service("RouterEntityManager")
        self.set_local_addr(sk.G.profile.get('local_addr'))
        assert self.m_RouterManager is not None

    @property
    def PeerInfo(self):
        return self.m_dictPeerInfo

    @property
    def PeerAddr(self):
        return self.m_dictPeerInfo.get('local_addr')

    def on_connected(self):
        print("=========================")

    def on_messager_lost(self, messager):
        super().on_messager_lost(messager)
        self.m_RouterManager.UnRegisterPeerInRouter(self)

    @rpc()
    def RegisterPeerInRouter(self, dictPeerInfo):
        print("RegisterPeerInRouter=========================", dictPeerInfo)
        self.m_dictPeerInfo = dictPeerInfo
        self.m_RouterManager.RegisterPeerInRouter(self)
        self.rpc_stub.OnRegisteredInRouter()

    def forward(self, dest, message):
        # forward message
        self.m_RouterManager.Forward(dest, message)
