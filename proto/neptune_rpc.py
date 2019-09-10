from transport.neptune import Neptune
from logf import logger
from .protobuf.output.rpc_pb2 import RPC, Response, Request
from google.protobuf import service


class NeptuneRpcChannel(service.RpcChannel):
    '''
    RpcChannel
    '''
    def __init__(self, manager):
        self.manager = manager
        self.sessions = {}
        self.sid = 0

    def gen_new_sid(self):
        self.sid += 1
        self.sid = max(self.sid, 0)
        return self.sid

    async def CallMethod(self, method_descriptor, rpc_controller, request, response_class, done):
        rpc = RPC()
        rpc.request.service = method_descriptor.containing_service.name
        rpc.request.method = method_descriptor.name
        rpc.request.args = request.SerializeToString()
        rpc.sid = self.gen_new_sid()
        logger.debug("rpc CallMethod: {}".format(rpc))
        if done:
            self.sessions[rpc.sid] = (response_class, done)

        await self.manager.send(rpc.SerializeToString())
        # Test
        # await self.manager.on_message(rpc.SerializeToString())

    async def on_response(self, rpc):
        if rpc.HasField("response"):
            sess = self.sessions.pop(rpc.sid, None)
            if sess:
                cls, done = sess
                response = cls()
                response.ParseFromString(rpc.response.response)
                done(response)
                return

        logger.error("invalid response: {}".format(rpc))


class NeptuneRpcCaller:
    '''
    RpcCaller, decode rpc request and call corresponding method.
    '''
    class ResponseCallback:
        __slots__ = ['sid', 'response']

        def __init__(self, sid):
            self.sid = sid
            self.response = None

        def __call__(self, response):
            self.response = response

    def __init__(self, manager):
        self.manager = manager

    async def call(self, rpc):
        service = self.manager.get_service(rpc.request.service)
        method = service.GetDescriptor().FindMethodByName(rpc.request.method)

        request_args = service.GetRequestClass(method)()
        request_args.ParseFromString(rpc.request.args)

        controller = None
        callback = self.ResponseCallback(rpc.sid)

        # synchronously call method
        co = service.CallMethod(method, controller, request_args, callback)

        # await if method is a coroutine, i.e. asynchronous method
        if asyncio.iscoroutine(co):
            await co

        # send response
        if callback.response:
            await self.send_response(callback.sid,  callback.response)

    async def send_response(self, sid, response):
        rpc = RPC()
        rpc.response.response = response.SerializeToString()
        rpc.sid = sid
        logger.debug("send response: {}".format(rpc))
        # await self.manager.on_message(rpc.SerializeToString())
        await self.manager.send(rpc.SerializeToString())


class NeptuneRpc(Neptune):

    def __init__(self, *args, **kargs):
        services = kargs.pop('services')
        super().__init__(*args, **kargs)
        self.services = {}
        self.rpc_channel = NeptuneRpcChannel(self)
        self.rpc_caller = NeptuneRpcCaller(self)
        self.sid = 0
        for s in services:
            self.services[s.GetDescriptor().name] = s

    def get_service(self, service):
        return self.services.get(service)

    async def on_message(self, msg):
        rpc = RPC()
        rpc.ParseFromString(msg)

        if rpc.HasField("request"):
            await self.rpc_caller.call(rpc)
        elif rpc.HasField("response"):
            await self.rpc_channel.on_response(rpc)
        else:
            logger.error("unknown messge, content: {}".format(rpc))


# Test
import asyncio
from service.foo import FooService, FooRequest, Foo_Stub
def main():
    foo = FooService()
    nep = NeptuneRpc(services=[foo])

    rpc = RPC()
    request = rpc.request

    request.service = "Foo"
    request.method = "Foo"
    args = FooRequest()
    args.message = "hello"
    request.args = args.SerializeToString()
    rpc.sid = 1

    async def func():
        foo_service = Foo_Stub(nep.rpc_channel)
        controller = None
        await foo_service.Foo(controller, args, lambda _: print("callback"))
#        await nep.on_message(rpc.SerializeToString())
        # if rpc.service and rpc.method:
        #     service = services.get(rpc.service)
        #     method = service.GetDescriptor().FindMethodByName(rpc.method)
        #     request = service.GetRequestClass(method)()
        #     request.ParseFromString(rpc.request)
        #     controller = None
        #     await service.CallMethod(method, controller, request, lambda: print("callback"))
    asyncio.run(func())
