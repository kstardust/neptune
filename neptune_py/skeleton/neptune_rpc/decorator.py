import functools


def rpc(meta=None):
    def __layer1(func):
        @functools.wraps(func)
        def __layer2(*args, **kwargs):
            return func(*args, **kwargs)
        __layer2.__nprpc_meta__ = meta
        __layer2.__nprpc__ = True
        return __layer2
    return __layer1
