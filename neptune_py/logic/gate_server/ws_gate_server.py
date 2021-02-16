import asyncio
from neptune_py.skeleton.skeleton import NeptuneServerSkeleton
from neptune_py.skeleton.messager import NeptuneMessagerManager
from neptune_py.skeleton.transporter.neptune_tlv import NeptuneTlvClient
from neptune_py.skeleton.transporter.neptune_wsrpc import NeptuneWSService, NeptuneWSRpc
from . router_in_gate import NeptuneRouterInGate
from . client_in_gate import NeptuneClientInGate


class NeptuneWebsocketGateServer:
    def __init__(self, name):
        self.name = name
        self.init_services()

    def init_services(self):
        np_server = NeptuneServerSkeleton(self.name)
        np_server.profile = {
            "addr4client": ('127.0.0.1', '1317'),
            "local_addr": "13:gate1"
        }

        np_server.client_manager = NeptuneMessagerManager(NeptuneClientInGate)
        ws_server = NeptuneWSService(*np_server.profile['addr4client'], "NeptuneWSService")
        wsrpc_service = NeptuneWSRpc('/13', np_server.client_manager)
        ws_server.add_route(wsrpc_service)

        np_server.add_service(ws_server)
        np_server.add_service(wsrpc_service)
        np_server.add_service(NeptuneTlvClient('0.0.0.0', '1316', NeptuneMessagerManager(NeptuneRouterInGate)))
        self.np_server = np_server

    async def run(self):
        await asyncio.gather(
            self.np_server.run()
        )
