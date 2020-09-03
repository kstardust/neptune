import grpc.experimental.aio as agrpc
from . skeleton import NeptuneServiceSkeleton


class NeptuneGRPCService(NeptuneServiceSkeleton):
    def add_to_server(self):
        raise NotImplementedError()


class GRPCServerService(NeptuneServiceSkeleton):
    def __init__(self, bind_address):
        super().__init__("grpc")
        self.bind_address = bind_address
        self._services = set()

    def init(self):
        # DO NOT call agrpc.server() in __init__, because that time wei are not inside any
        # asyncio loop, it then will create a loop.
        self.grpc_server = agrpc.server()
        self.grpc_server.add_insecure_port(self.bind_address)
        for service in self._services:
            service.add_to_server(self.grpc_server)

    async def logic(self):
        await self.grpc_server.start()
        await self.grpc_server.wait_for_termination()

    async def finish(self):
        await self.grpc_server.stop(None)

    def add_service(self, grpc_service: NeptuneGRPCService):
        # postpone add_to_server until self.grpc_server was created,
        self._services.add(grpc_service)
