import asyncio
import neptune_py.proto as proto
import grpc.experimental.aio as agrpc
from neptune_py.skeleton.skeleton import NeptuneServiceSkeleton


class Channel:
    def __init__(self, name, channel):
        self.name = name
        self.channel = channel
        self.stubs = {}

    def add_stub(self, name, stub):
        s = stub(self.channel)
        self.stubs[name] = s


class StubService(NeptuneServiceSkeleton):

    def __init__(self, dclient_service_name, name=None):
        super().__init__(name)
        self.discovery_client_service_name = dclient_service_name
        self.stub_channels = {}
        self._semaphore = asyncio.Queue()
        self._data = []

    def discovery_callback(self, data):
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
        # python will create a new obj for every bound method,
        # we store it here in order to call `remove_listener` later
        self._listener = self.discovery_callback
        discovery_client_service.add_listener(self._listener)

    async def finish(self):
        discovery_client_service = self.server.find_service(
            self.discovery_client_service_name
        )

        if discovery_client_service is not None:
            discovery_client_service.remove_listener(self._listener)

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
                stub_channel = Channel(identifier, channel)

                for service in server.Services:
                    s = getattr(proto, service + 'Stub', None)
                    if s is not None:
                        stub_channel.add_stub(service, s)
                        self.server.get_logger().debug(
                            f"register stub {service} to channel {identifier}"
                        )
                    else:
                        self.server.get_logger().debug(
                            f"unknown stub {service}"
                        )

                self.stub_channels[identifier] = stub_channel
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
            result = await self.stub_channels.get("type_any_13").stubs.get('Discovery').Echo(proto.EchoMsg(Msg="13"))
            print("echo", result)
