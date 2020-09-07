import asyncio
import grpc.experimental.aio as agrpc
from neptune_py.skeleton.skeleton import NeptuneServiceSkeleton


class StubService(NeptuneServiceSkeleton):

    def __init__(self, dclient_service_name, name=None):
        super().__init__(name)
        self.discovery_client_service_name = dclient_service_name
        self.stub_channels = {}
        self._semaphore = asyncio.Queue()
        self._data = []

    def discovery_callback(self, data: [int]):
        if data:
            self._data = data
            # notify logic coroutine to update stub channels
            if self._semaphore.empty():
                self._semaphore.put_nowait(1)

    def init(self):
        discovery_client_service = self.server.find_service(
            self.discovery_client_service_name
        )
        assert discovery_client_service is not None
        discovery_client_service.add_listener(self.discovery_callback)

    @classmethod
    def identifier_of_channel(cls, type_, id_):
        return '_'.join([type_, id_])

    async def update(self):
        try:
            for server in self._data:
                identifier = self.identifier_of_channel(server.Type, str(server.Id))
                if identifier in self.stub_channels:
                    continue
                channel = agrpc.insecure_channel(server.Address)
                await channel.channel_ready()
                self.stub_channels[identifier] = channel
                self.server.get_logger().debug(
                    f"connected to new channel {identifier}, {server.Address}"
                )
        except Exception as e:
            self.server.get_logger().error(
                f'exception occured during handling data'
            )
            self.server.get_logger().exception(e)

    async def logic(self):
        while True:
            await self._semaphore.get()
            await self.update()
