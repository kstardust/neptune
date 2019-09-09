import asyncio
from proto.protobuf.output.foo_pb2 import (
    Foo, FooRequest, FooResponse, Foo_Stub
)


class FooService(Foo):
    async def Foo(self, rpc_controller, request, done):
        response = FooResponse()
        response.message = "foo_" + request.message
        done(response)
