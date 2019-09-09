import asyncio
from proto.protobuf.output.bar_pb2 import (
    Bar, BarRequest, BarResponse, Bar_Stub
)


class BarService(Bar):
    async def Bar(self, rpc_controller, request, done):
        res = BarResponse()
        res.message = "bar_" + request.message
        done(res)
