"""
Don't perform consecutive calls (i.e. perform two
remote calls without consume the call_chain), otherwise
the later call will override the former call_chain if
they are from a common parent node, cause all sub nodes
share the same call_chain in parent node.

This will be improved in future version.
"""
import json


class NeptuneRpcError:
    class NeptuneRpcEmptyCallChain(Exception):
        pass

    class NeptuneRpcInvalidMessager(Exception):
        pass


class NeptuneNestedRpcStub:
    NestedNeptuneRpcPrefix = 'Nested'

    def __init__(self, sender, parent=None, encoder=json.dumps):
        '''
        a sender can write message(e.g. sending network package)
        i.e. sender is a transmitter for remote call
        '''
        self._call_chain = []
        self.parent = parent

        if self.parent is not None:
            # inherit from parent
            self.sender = parent.sender
            self.encoder = parent.encoder
            self._call_chain = parent._call_chain
        else:
            self.sender = sender
            self.encoder = encoder
        if self.sender is None:
            raise NeptuneRpcError.NeptuneRpcInvalidSender('sender is None')

    def __call__(self, *args):
        if not self._call_chain:
            raise NeptuneRpcError.NeptuneRpcEmptyCallChain('empty call chain')

        current_call = self._call_chain[-1]
        current_call[1] = args
        func_name, *_ = current_call

        if func_name.startswith(self.NestedNeptuneRpcPrefix):
            return self
        else:
            self.perform_rpc()

    def perform_rpc(self):
        self.sender(self.encoder(self._call_chain))

    def __getattr__(self, func_name):
        print(f'new node {func_name}')
        # extending current call chain and propagating it to child node

        # call chain node: format [func_name, args]
        self._call_chain.append([func_name, None])
        setattr(self, func_name, NeptuneNestedRpcStub(None, self))

        # pop last call stack(it belongs to child node)
        self._call_chain = self._call_chain[:-1]
        return getattr(self, func_name)


class NeptuneNestedRpc:
    def __init__(self, entity, decoder=json.loads):
        self._entity = entity
        self.decoder = decoder

    def execute(self, call_chain_data):
        slot = self._entity
        call_chain = self.decoder(call_chain_data)
        for call in call_chain:
            func_name, args = call
            slot = getattr(slot, func_name)(*args)


# ----------------------- Test Code

class Empty:
    pass


def FinalCall(*args):
    print(f'FinalCall {args}')


def NestedTestCall4(*args):
    print(f'NestedTestCall4 {args}')
    obj = Empty()
    obj.FinalCall = FinalCall
    return obj


def NestedTestCall3(*args):
    print(f'NestedTestCall3 {args}')
    obj = Empty()
    obj.FinalCall = FinalCall
    return obj


def NestedTestCall2(*args):
    print(f'NestedTestCall2 {args}')
    obj = Empty()
    obj.NestedTestCall3 = NestedTestCall3
    obj.NestedTestCall4 = NestedTestCall4
    return obj


class TestEntity:
    def NestedTestCall1(self, arg1, arg2):
        print(f'NestedTestCall1 {(arg1, arg2)}')
        obj = Empty()
        obj.NestedTestCall2 = NestedTestCall2
        return obj


class Sender:
    def __init__(self):
        self.message = None

    def __call__(self, message):
        self.message = message


if __name__ == '__main__':
    slot = NeptuneNestedRpc(TestEntity())

    sender = Sender()
    stub = NeptuneNestedRpcStub(sender, 13)
    stub.NestedTestCall1('13', '13').NestedTestCall2('13', {'13': 13}).NestedTestCall3('13').FinalCall(13)

    slot.execute(sender.message)
    stub.NestedTestCall1('1', '13').NestedTestCall2('13', {'1': 13}).NestedTestCall4('13').FinalCall(13)
    slot.execute(sender.message)
