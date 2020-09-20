import json


class NeptuneRPCProxy:
    def call(self, func_name, args_data):
        pass


class NeptuneRPC:
    def __init__(self, backend: NeptuneRPCProxy):
        self._backend = backend

    def __getattr__(self, func_name):
        def _rpc_call(*args):
            self._backend.call(func_name, args)
        return _rpc_call


class NeptuneJSONRPC(NeptuneRPCProxy):
    def call(self, func_name, args_data):
        print(json.dumps(args_data))


if __name__ == '__main__':
    rpc = NeptuneRPC(NeptuneRPCProxy(13))
    import datetime
    rpc.TestRPCCallabc(1, datetime.datetime.now(), [13, 13], {"ab": "cd"})
