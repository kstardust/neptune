from neptune_py.skeleton.entity.entity import NeptuneEntityBase
import neptune_py.skeleton.skeleton as sk
import neptune_py.skeleton.neptune_rpc.remote_call as remote_call
from neptune_py.skeleton.messager import NeptuneMessageType
from neptune_py.skeleton.neptune_rpc.decorator import rpc
from neptune_py.common import EUniversalMessageField
import json


class NeptuneClientInGate(NeptuneEntityBase):
    def __init__(self, entity_id, rpc_exec=True):
        super().__init__(entity_id, rpc_exec)
        self.m_dictProfile = sk.G.profile
        self.set_local_addr(self.m_dictProfile.get('local_addr'))
        # messges from ws client is a string, not a bytes array
        self.rpc_executor = remote_call.NeptuneNestedRpc(self, decoder=remote_call.JsonStringDecoder) if rpc_exec else None
        self.m_LobbyServerAddr = None
        self.m_GameServerAddr = None
        self.m_GameServerRpc = None
        self.m_LobbyServerRpc = None
        self.m_GlobalID = None

    def on_connected(self):
        pass
        # self.rpc_stub.TestRpc(1, "13", [1, 2, 3])

    @rpc()
    def Login(self, strToken):
        self.m_GlobalID = strToken
        self.m_LobbyServerAddr = ':'.join([self.subnet, "game1", self.m_GlobalID])
        self.m_GameServerAddr = ':'.join([self.subnet, "game1", self.m_GlobalID])
        self.m_GameServerRpc = self.GetUniversalRpcStub(self.m_GameServerAddr)
        self.m_LobbyServerRpc = self.GetUniversalRpcStub(self.m_LobbyServerAddr)
        self.logger.info("login token {}".format(strToken))

    @rpc()
    def GetLobbyServerPlayer(self):
        return self.m_LobbyServerRpc

    @rpc()
    def GetGameServerPlayer(self):
        return self.m_GameServerRpc

    @rpc()
    def TestRpc(self, a, b):
        print("testrpc", a, b)

    @property
    def rpc_stub(self):
        if self._rpc_stub is None:
            if self.messager is None:
                self.logger.error("canont create rpc_stub, this entity doest have a messager")
                return

            self._rpc_stub = remote_call.NeptuneNestedRpcStub(
                lambda message: self.send_message(
                    None,
                    message
                ),
                encoder=remote_call.JsonStringEncoder
            )
        return self._rpc_stub

    def GetUniversalRpcStub(self, dest_addr):
        Router = sk.G.GetRouter()
        if Router is None:
            self.logger.error("no gate!!!!")
            return

        if dest_addr not in self._universal_rpc_stubs:
            if Router.messager is None:
                self.logger.error("cannot create Universal rpc_stub, this entity doest have a messager")
                return

            self._universal_rpc_stubs[dest_addr] = remote_call.NeptuneNestedRpcStub(
                lambda message: Router.send_message(
                    NeptuneMessageType.NeptuneMessageTypeForward,
                    json.dumps({
                        EUniversalMessageField.Destination: dest_addr,
                        EUniversalMessageField.Source: self.local_addr,
                        EUniversalMessageField.Payload: message
                    }).encode('utf-8'),
                ),
                encoder=remote_call.JsonStringEncoder
            )

        return self._universal_rpc_stubs[dest_addr]
