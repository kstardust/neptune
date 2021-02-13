import asyncio

from .game_server import Neptune


# class TestingGameEntity(NeptuneGameEntity):
#     def Update(self, time_delta):
#         return
#         print(f"Update {self.entity_id} {time_delta}")

#     def FixedUpdate(self):
#         return
#         print(f"FixedUpdate {self.entity_id}")

#     def LateUpdate(self, time_delta):
#         return
#         print(f"LateUpdate {self.entity_id} {time_delta}")


# from neptune_py.skeleton.entity.entity import NeptuneEntityBase
# class EchoEntity(NeptuneEntityBase):
#     def on_message(self, message):
#         print(message)
#         self.messager.write_message(message.mtype, message.message)


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
