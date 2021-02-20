import asyncio
from neptune_py.skeleton.entity.entity import NeptuneEntityBase
import neptune_py.skeleton.skeleton as sk
from neptune_py.skeleton.neptune_rpc.decorator import rpc
from neptune_py.skeleton.skeleton import NeptuneServerSkeleton
from neptune_py.skeleton.messager import NeptuneMessagerManager
from neptune_py.skeleton.transporter.neptune_tlv import NeptuneTlvClient
from neptune_py.etc.config import get_profile


class NeptuneRouterInGameServer(NeptuneEntityBase):

    def __init__(self, entity_id, rpc_exec=True):
        super().__init__(entity_id, rpc_exec)
        self.m_dictProfile = sk.G.profile
        self.set_local_addr(self.m_dictProfile.get('local_addr'))

    def on_connected(self):
        self.rpc_stub.RegisterPeerInRouter(self.m_dictProfile)

    @rpc()
    def OnRegisteredInRouter(self):
        print("OnRegisteredInRouter")
        self.GetUniversalRpcStub("13:game1:").TestUniversalRpc()

    @rpc()
    def TestUniversalRpc(self):
        print("TestUniversalRpc")

    def forward_entity(self, GlobalID, message):
        Entity = sk.G.GetEntity(GlobalID)
        if Entity:
            Entity.rpc_executor.execute(message)
            return
        self.logger.error("no such entity: {}".format(GlobalID))


class GameServerSkeleton(NeptuneServerSkeleton):
    def init(self):
        self.m_dictEntities = {}

    def GetEntity(self, GlobalID):
        return self.m_dictEntities.get(GlobalID)

    def AddEntity(self, GlobalID, Entity):
        self.m_dictEntities[GlobalID] = Entity

    def RemoveEntity(self, GlobalID):
        self.m_dictEntities.pop(GlobalID, None)


class Neptune:
    def __init__(self, name):
        self.name = name
        self.init_services()

    def init_services(self):
        np_server = GameServerSkeleton(self.name)
        np_server.init()
        # self.client_manager = NeptuneGamePlayerManager()

        # game_master = GameMaster(60)
        # e1 = TestingGameEntity()
        # e2 = TestingGameEntity()
        # game_master.AddEntity(e1)
        # game_master.AddEntity(e2)

        # np_server.add_service(game_master)
        # np_server.add_service(Introspector())
        # np_server.add_service(NeptuneTlvService('0.0.0.0', '1313', self.client_manager))
        router_addr = np_server.profile.get('router_addr')
        router_net_addr = get_profile(router_addr).get('addr4port')

        np_server.add_service(NeptuneTlvClient('0.0.0.0', '1316', NeptuneMessagerManager(NeptuneRouterInGameServer)))
        self.np_server = np_server

    async def run(self):
        await asyncio.gather(
            self.np_server.run()
        )
