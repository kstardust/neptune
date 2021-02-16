import asyncio
from neptune_py.skeleton.skeleton import NeptuneServerSkeleton
from neptune_py.skeleton.messager import NeptuneMessagerManager
from neptune_py.skeleton.transporter.neptune_tlv import NeptuneTlvClient
from neptune_py.skeleton.transporter.neptune_wsrpc import NeptuneWSService, NeptuneWSRpc
from . router_in_gate import NeptuneRouterInGate
from . client_in_gate import NeptuneClientInGate


class NeptuneGateSkeleton(NeptuneServerSkeleton):

    def init(self):
        self.m_Gate = None
        self.profile = {
            "addr4client": ('127.0.0.1', '1317'),
            "local_addr": "13:gate1:"
        }

        self.client_manager = NeptuneMessagerManager(NeptuneClientInGate)
        ws_server = NeptuneWSService(*self.profile['addr4client'], "NeptuneWSService")
        wsrpc_service = NeptuneWSRpc('/13', self.client_manager)
        ws_server.add_route(wsrpc_service)

        self.add_service(ws_server)
        self.add_service(wsrpc_service)
        self.add_service(NeptuneTlvClient('0.0.0.0', '1316', NeptuneMessagerManager(NeptuneRouterInGate)))

    def SetRouter(self, gate):
        self.m_Gate = gate

    def GetRouter(self):
        return self.m_Gate


class NeptuneWebsocketGateServer:
    def __init__(self, name):
        self.name = name
        self.init_services()

    def init_services(self):
        np_server = NeptuneGateSkeleton(self.name)
        np_server.init()
        self.np_server = np_server

    async def run(self):
        await asyncio.gather(
            self.np_server.run()
        )
