import neptune_py.skeleton.neptune_rpc.remote_call as remote_call
from neptune_py.skeleton.messager import NeptuneMessageType, NeptuneMessageTuple
from neptune_py.skeleton import utils


class NeptuneEntityBase:

    def __init__(self):
        self.rpc_executor = remote_call.NeptuneNestedRpc(self)

    def bind_messager(self, messager):
        utils.color_print(utils.AnsiColor.OKGREEN, 'bind messager')

        self.messager = messager
        self.rpc_stub = remote_call.NeptuneNestedRpcStub(
            lambda message: self.messager.write_message(
                NeptuneMessageType.NeptuneMessageTypeCall,
                message
            )
        )
        self.on_connected()

    def on_connected(self):
        pass

    @property
    def RpcStub(self):
        return self.rpc_stub

    def on_messager_lost(self, messager):
        self.rpc_stub = None
        utils.color_print(utils.AnsiColor.WARNING, 'messager lost')

    def on_message(self, message: NeptuneMessageTuple):
        if message.type == NeptuneMessageType.NeptuneMessageTypeCall:
            # remote call
            self.rpc_executor.execute(message.message)
            return

        utils.color_print(utils.AnsiColor.FAIL, f'unknown message {message}')
