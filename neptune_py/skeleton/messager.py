import collections
from neptune_py.skeleton import utils

NeptuneMessageTuple = collections.namedtuple('NeptuneMessageTuple', ['type', 'message'])


class NeptuneMessageType:
    NeptuneMessageTypeCall = 1


class NeptuneWriterBaseAbstract:
    def write(self, message_type: NeptuneMessageType, message):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()


class NeptuneMessager:
    def __init__(self, id_, manager, read_writer, entity_cls):
        self.manager = manager
        self.entity_cls = entity_cls
        self.id_ = id_
        self.read_writer = read_writer
        self.entity = None

    def write_message(self, mtype, message):
        self.read_writer.write(mtype, message)

    def on_message(self, message):
        self.entity.on_message(message)

    def on_connected(self):
        self.entity = self.entity_cls()
        self.entity.bind_messager(self)

    def on_error(self, error):
        raise NotImplementedError()

    def on_disconnected(self):
        self.entity.on_messager_lost(self)

    def close(self):
        raise NotImplementedError()


class NeptuneMessagerManager:
    def __init__(self, entity_cls):
        self.entity_cls = entity_cls
        self.messagers = {}

    def on_connected(self, id_, read_writer):
        messager = NeptuneMessager(
            id_, self, read_writer, self.entity_cls
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
