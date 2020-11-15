import collections
import abc
import struct
from neptune_py.skeleton import utils

NeptuneMessageTuple = collections.namedtuple('NeptuneMessageTuple', ['mtype', 'message'])


class NeptuneMessageType:
    NeptuneMessageTypeNone = 0
    NeptuneMessageTypeNornmal = 1
    NeptuneMessageTypeCall = 2


class NeptuneWriterBaseAbstract:
    @abc.abstractmethod
    def write(self, message):
        raise NotImplementedError()

    @abc.abstractmethod
    def close(self):
        raise NotImplementedError()


class NeptuneMessager:
    MessageTypeFormat = '!H'
    MessageTypeSize = struct.calcsize(MessageTypeFormat)

    def __init__(self, id_, manager, writer: NeptuneWriterBaseAbstract, entity_cls):
        self.manager = manager
        self.entity_cls = entity_cls
        self.id_ = id_
        self.writer = writer
        self.entity = None

    def write_message(self, mtype, message):
        self.writer.write(struct.pack(self.MessageTypeFormat, mtype) + message)

    def on_message(self, message):
        if len(message) < self.MessageTypeSize:
            utils.color_print(utils.AnsiColor.FAIL, "invalid message, cannot unpack message type")
            self.close()
            return
        mtype, *_ = struct.unpack(self.MessageTypeFormat, message[:self.MessageTypeSize])
        self.entity.on_message(NeptuneMessageTuple(mtype=mtype, message=message[self.MessageTypeSize:]))

    def on_connected(self):
        self.entity = self.entity_cls()
        self.entity.bind_messager(self)

    def on_error(self, error):
        raise NotImplementedError()

    def on_disconnected(self):
        self.entity.on_messager_lost(self)

    def close(self):
        self.writer.close()


class NeptuneMessagerManager:
    def __init__(self, entity_cls):
        self.entity_cls = entity_cls
        self.messagers = {}

    def on_connected(self, id_, writer: NeptuneWriterBaseAbstract):
        messager = NeptuneMessager(
            id_, self, writer, self.entity_cls
        )
        messager.on_connected()
        self.messagers[id_] = messager

    def on_message(self, id_, message):
        messager = self.messagers.get(id_)
        if messager is None:
            # TODO invaild, close
            pass

        messager.on_message(message)

    def on_disconnected(self, id_):
        utils.color_print(utils.AnsiColor.FAIL, f'disconnected============{id_}')
        self.remove_messager(id_)

    def remove_messager(self, id_):
        messager = self.messagers.pop(id_, None)
        if messager is not None:
            messager.on_disconnected()
