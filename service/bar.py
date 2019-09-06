import asyncio
from proto.protobuf.output.bar_pb2 import (
    Bar, BarRequest, BarResponse
)


class BarService(Bar):
    async def Bar(self, rpc_controller, request, done):
        await asyncio.sleep(1)
        print(request.message)
        done()
