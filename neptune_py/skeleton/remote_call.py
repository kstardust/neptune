"""
Don't perform consercutive calls (i.e. perform two
remote call without consume the call_chain), otherwise
the later call will override the former call_chain if
they are from a common parent node, cause all sub nodes
share the same call_chain in parent node.

This will be improved in future version.
"""


class NeptuneRpcError:
    class NeptuneRpcEmptyCallChain(Exception):
        pass

    class NeptuneRpcInvalidMessager(Exception):
        pass


class NeptuneNestedRpcStub:
    NestedNeptuneRpcPrefix = 'Nested'

    def __init__(self, messager, parent=None):
        '''
        a messager can write message(e.g. sending network package)
        i.e. messager is a transmitter for remote call
        '''
        self._call_chain = []
        self.parent = parent
        if messager is None and self.parent is not None:
            # inherit from parent
            self.messager = parent.messager
            # TODO: Do we really need to copy call_chain?
            # child node rpc won't touch the element of parent node in call_chain,
            # it's not necessary to copy
            self._call_chain = parent._call_chain
        else:
            self.messager = messager
        if self.messager is None:
            raise NeptuneRpcError.NeptuneRpcInvalidMessager('messager is None')

    def __call__(self, *args):
        if not self._call_chain:
            raise NeptuneRpcError.NeptuneRpcEmptyCallChain('empty call chain')

        current_call = self._call_chain[-1]
        current_call[1] = args
        func_name, *_ = current_call

        if func_name.startswith(self.NestedNeptuneRpcPrefix):
            return self
        else:
            # actually perform remote call
            print(f'neptune Rpc call {self._call_chain}')
            # test code
            return self._call_chain

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
    def __init__(self, entity):
        self._entity = entity

    def execute(self, call_chain):
        slot = self._entity
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
    return obj


class TestEntity:
    def NestedTestCall1(self, arg1, arg2):
        print(f'NestedTestCall1 {(arg1, arg2)}')
        obj = Empty()
        obj.NestedTestCall2 = NestedTestCall2
        return obj


if __name__ == '__main__':
    slot = NeptuneNestedRpc(TestEntity())

    stub = NeptuneNestedRpcStub(13)
    call_chain = stub.NestedTestCall1('13', '13').NestedTestCall2('13', {'13': 13}).NestedTestCall3('13').FinalCall(13)

    slot.execute(call_chain)
    stub.NestedTestCall1('1', '13').NestedTestCall2('13', {'1': 13}).NestedTestCall4('13').FinalCall(13)
    slot.execute(call_chain)
