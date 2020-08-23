import grpc.experimental.aio as agrpc
import grpc
import asyncio
import concurrent
from neptune_py.proto import discovery_service_pb2
from neptune_py.proto import error_pb2
from neptune_py.proto import discovery_service_pb2_grpc


class DiscoveryService(discovery_service_pb2_grpc.DiscoveryServicer):
    async def Register(self, request, context):
        print("Register", request)
        return discovery_service_pb2.RegisterResponse(
            Error=error_pb2.CommonError(),
            Keepalive=10
        )

    async def _keepalive_reader(self, request_iterator):
        async for request in request_iterator:
            print("request: ", request)

    async def Keepalive(self, request_iterator, context):
        print("hello")
        input_ = asyncio.create_task(self._keepalive_reader(request_iterator))
        for i in range(10):
            yield discovery_service_pb2.Servers(
                Servers=[discovery_service_pb2.Server(Type="response", Id=i)]
            )
        # await context.abort(grpc.StatusCode.CANCELLED)
        await input_


async def serve():
    server = agrpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    discovery_service_pb2_grpc.add_DiscoveryServicer_to_server(DiscoveryService(), server)
    server.add_insecure_port("0.0.0.0:1313")
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(serve())
