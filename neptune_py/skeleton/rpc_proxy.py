import json


class NeptuneRPCProxy:
    def __init__(self, func_name):
        self.func_name = func_name

    def __call__(self, *args):
        print(f"rpc call {self.func_name} with args {args}")


class NeptuneRPC:
    def __init__(self, rpc_cls):
        self._backend_cls = rpc_cls
        self._rpcs = {}

    def __getattr__(self, func_name):
        return self._backend_cls(func_name)


class NeptuneJSONRPC(NeptuneRPCProxy):
    def __call__(self, *args_data):
        print(self.func_name, json.dumps(args_data))


if __name__ == '__main__':
    rpc = NeptuneRPC(NeptuneJSONRPC)
    import datetime
    rpc.TestRPCCallabc(1, [13, 13], {"ab": "cd"})
