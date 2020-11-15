from neptune_py.skeleton.entity.entity import NeptuneEntityBase
import neptune_py.skeleton.neptune_rpc.remote_call as remote_call
from neptune_py.skeleton.messager import NeptuneMessageType
import json


def decoder(data):
    data = json.loads(data)
    method_name = data['methodName']
    args = [json.loads(arg) for arg in data['args']]
    return [[method_name, args]]


def encoder(call_chain):
    [method_name, args] = call_chain[0]
    csharp_dict_data = {
        "methodName": method_name,
        "args": [json.dumps(arg) for arg in args]
    }
    return json.dumps(csharp_dict_data)


class GameServerPlayer(NeptuneEntityBase):

    def __init__(self):
        super().__init__()
        self.rpc_executor = remote_call.NeptuneNestedRpc(self, decoder=decoder)

    @property
    def rpc_stub(self):
        if self._rpc_stub is None:
            if self.messager is None:
                self.logger.error("canont create rpc_stub, this entity doest have a messager")
                return

            self._rpc_stub = remote_call.NeptuneNestedRpcStub(
                lambda message: self.messager.write_message(
                    NeptuneMessageType.NeptuneMessageTypeCall,
                    message.encode('utf-8')
                ),
                encoder=encoder
            )
        return self._rpc_stub

    def PlayerRpcTesting(self, a, b, c):
        self.rpc_stub.GameServerRpcRespTesting(a, b, c)
