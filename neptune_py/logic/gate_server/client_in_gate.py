from neptune_py.skeleton.entity.entity import NeptuneEntityBase
import neptune_py.skeleton.skeleton as sk
import neptune_py.skeleton.neptune_rpc.remote_call as remote_call
from neptune_py.skeleton.messager import NeptuneMessageType
from neptune_py.skeleton.neptune_rpc.decorator import rpc


class NeptuneClientInGate(NeptuneEntityBase):
    def __init__(self, entity_id, rpc_exec=True):
        super().__init__(entity_id, rpc_exec)
        self.m_dictProfile = sk.G.profile
        self.set_local_addr(self.m_dictProfile.get('local_addr'))
        # messges from ws client is a string, not a bytes array
        self.rpc_executor = remote_call.NeptuneNestedRpc(self, decoder=remote_call.JsonStringDecoder) if rpc_exec else None

    def on_connected(self):
        self.rpc_stub.TestRpc(1, "13", [1, 2, 3])

    def GetUniversalRpcStub(self, dest_addr):
        # client entity is not allow to use universal rpc stub
        raise NotImplementedError()

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
