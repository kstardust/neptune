import struct
from google.protobuf import service
from logf import logger
from transport.base import PeerAbstract


class NeptuneRpcChannel(service.RpcChannel):
    MetaField = struct.Struct('!H')

    def __init__(self, peer: PeerAbstract):
        super().__init__()
        self.peer = peer

    def CallMethod(self, method_descriptor, rpc_controller, request, response_class, done):
        logger.info("Call {}".fromat(method_descriptor))
        index = method_descriptor.index
        # FIXME: index limit
        data = request.SerializeToString()
        meta = self.MetaField.pack(index)
        self.peer.send(b''.join([meta, data]))

    def on_message(self, data):
        index = self.MetaField.unpack_from(data)
