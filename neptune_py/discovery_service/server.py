import grpc.experimental.aio as agrpc
import asyncio
import concurrent
import collections
from datetime import (datetime, timedelta)
from neptune_py.proto import discovery_service_pb2
from neptune_py.proto import error_pb2
from neptune_py.proto import discovery_service_pb2_grpc


Peer = collections.namedtuple('Peer', ['pid', 'last_seen', 'data'])


class PeerManager:
    def __init__(self, ttl=timedelta(seconds=10)):
        self.ttl = ttl
        self._peers = {}

    def expire(self):
        now = datetime.now()
        self._peers = {
            k: v
            for k, v in self._peers.items()
            if now - v.last_seen <= self.ttl
        }

    def register(self, id_, data):
        self.expire()
        if id_ in self._peers:
            return False
        self._peers[id_] = Peer(pid=id_, data=data, last_seen=datetime.now())
        return True

    def keepalive(self, id_):
        self.expire()
        if id_ not in self._peers:
            return False
        peer = self._peers[id_]
        peer.last_seen = datetime.now()
        return True

    @property
    def peers(self):
        self.expire()
        return [v.data for v in self._peers.values()]


class DiscoveryService(discovery_service_pb2_grpc.DiscoveryServicer):

    def __init__(self, ttl=timedelta(seconds=10)):
        self.peer_manager = PeerManager(ttl)
        self._peers = {}

    async def Register(self, request, context):
        print("Register", request)
        if self.peer_manager.register(request.Id, request):
            return discovery_service_pb2.RegisterResponse(
                Error=error_pb2.CommonError(
                    Code=error_pb2.FAILED,
                    Reason=f"pid {request.Id} already exists"
                ),
            )
        return discovery_service_pb2.RegisterResponse(
            Error=error_pb2.CommonError(),
            Keepalive=self.peer_manager._keepalive.total_seconds()
        )

    async def _keepalive_reader(self, request_iterator):
        async for request in request_iterator:
            self.peer_manager.keepalive(request.Id)

    async def Keepalive(self, request_iterator, context):
        print("hello")
        input_ = asyncio.create_task(self._keepalive_reader(request_iterator))
        while True:
            yield discovery_service_pb2.Servers(
                Servers=self.peer_manager.peers
            )
            await asyncio.sleep(self.peer_manager.ttl.total_seconds())
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
    pm = PeerManager()
    for i in range(10):
        pm.register(i, {"data": i})
    for p in pm.peers:
        print(p)
