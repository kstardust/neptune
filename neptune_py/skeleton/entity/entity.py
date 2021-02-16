import neptune_py.skeleton.neptune_rpc.remote_call as remote_call
from neptune_py.skeleton.messager import NeptuneMessageType, NeptuneMessageTuple
from neptune_py.skeleton import utils
from neptune_py.common import EUniversalMessageField
import json
import logging


class NeptuneEntityBase:

    def __init__(self, entity_id, rpc_exec=True):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.entity_id = entity_id
        self.rpc_executor = remote_call.NeptuneNestedRpc(self) if rpc_exec else None
        self.messager = None
        self._rpc_stub = None
        self._universal_rpc_stubs = {}
        self.local_addr = None

    def set_local_addr(self, addr):
        self.local_addr = addr
        self.subnet, *_ = addr.split(":")

    def bind_messager(self, messager):
        utils.color_print(utils.AnsiColor.OKGREEN, 'bind messager')

        self.messager = messager
        self.on_connected()

    def on_connected(self):
        pass

    def send_message(self, mtype, message):
        self.messager.write_message(mtype, message)

    def GetUniversalRpcStub(self, dest_addr):
        if dest_addr not in self._universal_rpc_stubs:
            if self.messager is None:
                self.logger.error("cannot create Universal rpc_stub, this entity doest have a messager")
                return

            self._universal_rpc_stubs[dest_addr] = remote_call.NeptuneNestedRpcStub(
                lambda message: self.send_message(
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

    @property
    def rpc_stub(self):
        if self._rpc_stub is None:
            if self.messager is None:
                self.logger.error("canont create rpc_stub, this entity doest have a messager")
                return

            self._rpc_stub = remote_call.NeptuneNestedRpcStub(
                lambda message: self.send_message(
                    NeptuneMessageType.NeptuneMessageTypeCall,
                    message
                )
            )
        return self._rpc_stub

    def on_messager_lost(self, messager):
        self._rpc_stub = None
        self.messager = None
        utils.color_print(utils.AnsiColor.WARNING, 'messager lost')

    def iamthedest(self, dest):
        return dest == self.local_addr

    def iamtheserver(self, dest):
        serverDest, _ = dest.rsplit(":", maxsplit=1)
        serverDest += ":"
        return serverDest == self.local_addr

    def forward(self, dest, message):
        raise NotImplementedError

    def forward_entity(self, GlobalID, payload):
        print("forward_entity", GlobalID, payload)

    def on_message(self, message: NeptuneMessageTuple):
        if message.mtype == NeptuneMessageType.NeptuneMessageTypeCall:
            # remote call
            if self.rpc_executor is None:
                self.logger.error("this entity cannot exec rpc")
                return
            self.rpc_executor.execute(message.message)
            return

        elif message.mtype == NeptuneMessageType.NeptuneMessageTypeForward:
            # forward message
            dictMessage = json.loads(message.message.decode('utf-8'))
            destAddr = dictMessage[EUniversalMessageField.Destination]
            if self.iamthedest(destAddr):
                payload = dictMessage[EUniversalMessageField.Payload].encode('utf-8')
                # srcAddr = dictMessage[EUniversalMessageField.Source]
                self.rpc_executor.execute(payload)
            elif self.iamtheserver(destAddr):
                payload = dictMessage[EUniversalMessageField.Payload].encode('utf-8')
                # srcAddr = dictMessage[EUniversalMessageField.Source]
                _, GlobalID = destAddr.rsplit(':', maxsplit=1)
                self.forward_entity(GlobalID, payload)
            else:
                self.forward(destAddr, message.message)
            return

        utils.color_print(utils.AnsiColor.FAIL, f'unknown message {message}')

    def Update(self):
        pass
