from neptune_py.skeleton.entity.entity import NeptuneEntityBase
from neptune_py.skeleton.neptune_rpc.decorator import rpc
import neptune_py.skeleton.skeleton as sk


class NeptuneRouterInRouterManager(NeptuneEntityBase):

    def __init__(self, entity_id, rpc_exec=True):
        super().__init__(entity_id, rpc_exec)
        self.m_dictRouters = {}
        self.m_dictRouterInfo = {}
        self.m_RouterManager = sk.G.find_service("RouterEntityManager")
        assert self.m_RouterManager is not None

    @property
    def RouterInfo(self):
        return self.m_dictRouterInfo

    @rpc()
    def RegisterRouter(self, dictRouterInfo):
        self.logger.info("RegisterRouter {}".format(dictRouterInfo))
        self.m_dictRouterInfo = dictRouterInfo
        self.m_RouterManager.RegisterRouter(self)

    def on_messager_lost(self, messager):
        super().on_messager_lost(messager)
        self.m_RouterManager.UnRegisterRouter(self)
