from transport.neptune import Neptune
from logf import logger
from .protobuf.output.rpc_pb2 import RPC, Response, Request


class NeptuneRpc(Neptune):

    class OutCall:
        __slots__ = ['cls', 'sid']

        def __init__(self, cls, sid):
            self.cls = cls
            self.sid = sid

    def __init__(self, *args, **kargs):
        services = kargs.pop('services')
#        super().__init__(*args, **kargs)
        self.services = {}
        self._outcalls = {}
        self.sid = 0
        for s in services:
            self.services[s.GetDescriptor().name] = s

    class ResponseCallback:
        __slots__ = ['sid', 'response']

        def __init__(self, sid):
            self.sid = sid
            self.response = None

        def __call__(self, response):
            self.response = response

    def gen_new_sid(self):
        self.sid += 1
        return self.sid

    async def CallMethod(self, method_descriptor, rpc_controller, request, done):
        # FIXME: use service_Stub and RpcChannel instead.
        rpc = RPC()
        rpc.request.service = method_descriptor.containing_service.name
        rpc.request.method = method_descriptor.name
        rpc.request.args = request.SerializeToString()
        rpc.sid = self.gen_new_sid()
        logger.debug("rpc CallMethod: {}".format(rpc))
        if done:
            self._outcalls[rpc.sid] = self.OutCall(rpc.sid, method_descriptor.output_type)

        # Test
        await self.on_message(rpc.SerializeToString())
#        await self.send(rpc.SerializeToString())

    async def on_message(self, msg):
        rpc = RPC()
        rpc.ParseFromString(msg)

        if rpc.HasField("request"):
            service = self.services.get(rpc.request.service)
            method = service.GetDescriptor().FindMethodByName(rpc.request.method)

            request_args = service.GetRequestClass(method)()
            request_args.ParseFromString(rpc.request.args)

            controller = None
            callback = self.ResponseCallback(rpc.sid)

            # synchronously call method
            co = service.CallMethod(method, controller, request_args, callback)

            # await if method is coroutine, i.e. asynchronous method
            if asyncio.iscoroutine(co):
                await co

            # send response
            if callback.response:
                await self.send_response(callback.sid,  callback.response)

        elif rpc.HasField("response"):
            logger.info("Response call {}".format(rpc))
        else:
            logger.error("invalid rpc, content: {}".format(rpc))

    async def send_response(self, sid, response):
        rpc = RPC()
        rpc.response.response = response.SerializeToString()
        rpc.sid = sid
        logger.debug("send response: {}".format(rpc))
        # await self.send(rpc.SerializeToString())


# Test
import asyncio
from service.foo import FooService, FooRequest
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
        await nep.CallMethod(foo.GetDescriptor().FindMethodByName("Foo"), None, args, None)
#        await nep.on_message(rpc.SerializeToString())
        # if rpc.service and rpc.method:
        #     service = services.get(rpc.service)
        #     method = service.GetDescriptor().FindMethodByName(rpc.method)
        #     request = service.GetRequestClass(method)()
        #     request.ParseFromString(rpc.request)
        #     controller = None
        #     await service.CallMethod(method, controller, request, lambda: print("callback"))
    asyncio.run(func())
