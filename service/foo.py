import asyncio
from proto.protobuf.output.foo_pb2 import (
    Foo, FooRequest, FooResponse
)


class FooService(Foo):
    async def Foo(self, rpc_controller, request, done):
        await asyncio.sleep(1)
        response = FooResponse()
        response.message = request.message
        done(response)
