import grpc.experimental.aio as agrpc
import asyncio
from neptune_py.proto import discovery_service_pb2
from neptune_py.proto import discovery_service_pb2_grpc


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
    import types, neptune_py
    print({k: v for k, v in neptune_py.proto.__dict__.items() if isinstance(v, types.ModuleType) and k.endswith('_grpc')})
    asyncio.run(request())
