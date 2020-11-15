import asyncio

from neptune_py.skeleton.skeleton import NeptuneServerSkeleton
from neptune_py.skeleton.utils import Introspector
from neptune_py.skeleton.messager import NeptuneMessagerManager
from neptune_py.skeleton.neptune_rpc.neptune_tlv import NeptuneTlvService
from .entity.game_server_player import GameServerPlayer


class Neptune:
    def __init__(self, name):
        self.name = name
        self.init_services()

    def init_services(self):
        np_server = NeptuneServerSkeleton(self.name)
        self.client_manager = NeptuneMessagerManager(GameServerPlayer)

        np_server.add_service(Introspector())
        np_server.add_service(NeptuneTlvService('0.0.0.0', '1313', self.client_manager))

        self.np_server = np_server

    async def run(self):
        await asyncio.gather(
            self.np_server.run()
        )


if __name__ == '__main__':
    np = Neptune('neptune')
    asyncio.run(np.run())

    # import yappi
    # yappi.set_clock_type('WALL')
    # try:
    #     with yappi.run():
    #         np = Neptune('neptune')
    #         asyncio.run(np.run())
    # finally:
    #     yappi.get_func_stats().print_all()
