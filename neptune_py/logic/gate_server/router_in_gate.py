from neptune_py.skeleton.entity.entity import NeptuneEntityBase
import neptune_py.skeleton.skeleton as sk
from neptune_py.skeleton.neptune_rpc.decorator import rpc


class NeptuneRouterInGate(NeptuneEntityBase):

    def __init__(self, entity_id, rpc_exec=True):
        super().__init__(entity_id, rpc_exec)
        self.m_dictProfile = sk.G.profile
        self.set_local_addr(self.m_dictProfile.get('local_addr'))

    def on_connected(self):
        self.rpc_stub.RegisterPeerInRouter(self.m_dictProfile)
        sk.G.SetRouter(self)

    @rpc()
    def OnRegisteredInRouter(self):
        print("OnRegisteredInRouter")
        self.GetUniversalRpcStub("13:game1:").TestUniversalRpc()
