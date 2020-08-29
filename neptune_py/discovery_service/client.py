import grpc.experimental.aio as agrpc
import asyncio
from neptune_py.proto import discovery_service_pb2
from neptune_py.proto import discovery_service_pb2_grpc


class Task:
    def __init__(self):
        self._tasks = []

    def add_task(self, task):
        task = asyncio.create_task(self._tasks.append(task))

    def cancel_all_tasks(self):
        try:
            for task in self._tasks:
                task.cancel()
        except asyncio.CancelledError as e:
            print(e)


class DiscoveryServiceClient:
    def __init__(self, server_address, sid, stype, address):
        self.server_address = server_address
        self.address = address
        self.stype = stype
        self.sid = sid
        self._done = False

    def done(self):
        self._done = True

    def is_done(self):
        return self._done

    async def _keepalive(self, interval):
        stream = self.grpc_stub.Keepalive()

        connect_task = asyncio.create_task(self._connect_service(stream))
        while True:
            await stream.write(
                discovery_service_pb2.KeepaliveRequest(Id=self.sid)
            )
            await asyncio.sleep(interval * 0.8)
        await connect_task

    async def _connect_service(self, stream):
        while True:
            response = await stream.read()
            print(response)

    async def start(self):
        self.grpc_channel = agrpc.insecure_channel(self.server_address)
        await self.grpc_channel.channel_ready()
        print(f"--------------connected to server {self.server_address}")
        self.grpc_stub = discovery_service_pb2_grpc.DiscoveryStub(
            self.grpc_channel
        )
        request = discovery_service_pb2.Server(
            Type=self.stype, Id=self.sid, Address=self.address
        )
        result = await self.grpc_stub.Register(request)

        if result.Error.Code:
            print(f"--------------error {result}")
            return

        keepalive_task = self._keepalive(result.Keepalive)
        await keepalive_task


async def request_stream(stream):
    for i in range(10):
        await stream.write(discovery_service_pb2.KeepaliveRequest(Id=13))


async def request():
    channel = agrpc.insecure_channel("0.0.0.0:1313")
    await channel.channel_ready()
    stub = discovery_service_pb2_grpc.DiscoveryStub(channel)

    request = discovery_service_pb2.Server(Type="type_any", Id=13)
    result = await stub.Register(request)
    print(result.Error.Code, result.Keepalive)

    stream = stub.Keepalive()
    await request_stream(stream)
    await stream.done_writing()
    while True:
        response = await stream.read()
        if response == agrpc.EOF:
            break
        print(response)


if __name__ == '__main__':
    ds = DiscoveryServiceClient("0.0.0.0:1313", 13, "type_any", "localhost:1111")
    asyncio.run(ds.start())
    import types, neptune_py
    print({k: v for k, v in neptune_py.proto.__dict__.items() if isinstance(v, types.ModuleType) and k.endswith('_grpc')})
    asyncio.run(request())
