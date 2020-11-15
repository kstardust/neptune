import neptune_py.skeleton.neptune_rpc.remote_call as remote_call
from neptune_py.skeleton.messager import NeptuneMessageType, NeptuneMessageTuple
from neptune_py.skeleton import utils
import logging


class NeptuneEntityBase:

    def __init__(self, rpc_exec=True):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.rpc_executor = remote_call.NeptuneNestedRpc(self) if rpc_exec else None
        self.messager = None
        self._rpc_stub = None

    def bind_messager(self, messager):
        utils.color_print(utils.AnsiColor.OKGREEN, 'bind messager')

        self.messager = messager
        self.on_connected()

    def on_connected(self):
        pass

    @property
    def rpc_stub(self):
        if self._rpc_stub is None:
            if self.messager is None:
                self.logger.error("canont create rpc_stub, this entity doest have a messager")
                return

            self._rpc_stub = remote_call.NeptuneNestedRpcStub(
                lambda message: self.messager.write_message(
                    NeptuneMessageType.NeptuneMessageTypeCall,
                    message
                )
            )
        return self._rpc_stub

    def on_messager_lost(self, messager):
        self._rpc_stub = None
        self.messager = None
        utils.color_print(utils.AnsiColor.WARNING, 'messager lost')

    def on_message(self, message: NeptuneMessageTuple):
        if message.mtype == NeptuneMessageType.NeptuneMessageTypeCall:
            # remote call
            if self.rpc_executor is None:
                self.logger.error("this entity cannot exec rpc")
                return
            self.rpc_executor.execute(message.message)
            return

        utils.color_print(utils.AnsiColor.FAIL, f'unknown message {message}')

    def Update(self):
        pass
