import asyncio
import traceback
import time
from neptune_py.skeleton.skeleton import NeptuneServiceSkeleton


class DoubleLinkedListNode:
    def __init__(self, key, value):
        self.next_node = None
        self.previous_node = None
        self.key = key
        self.value = value


class DoubleLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def is_empty(self):
        return self.head is None

    def Add(self, key, value):
        node = DoubleLinkedListNode(key, value)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            node.previous_node = self.tail
            self.tail.next_node = node
            self.tail = node
        return node

    def Delete(self, node: DoubleLinkedListNode):
        previous_node = node.previous_node
        next_node = node.next_node

        if node.previous_node is not None:
            node.previous_node.next_node = next_node
        else:
            # this node is the head
            self.head = next_node

        if node.next_node is not None:
            node.next_node.previous_node = previous_node
        else:
            # this node is the tail
            self.tail = previous_node

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node
            node = node.next_node

    def __str__(self):
        return "[" + ", ".join(f"({node.key}, {node.value})" for node in self) + "]"


class NeptuneGameEntity:
    def __init__(self):
        self.game_master = None
        self.entity_id = None
        self.active = True

    def Update(self):
        pass

    def LateUpdate(self):
        pass

    def FixedUpdate(self):
        pass

    def Destroy(self):
        pass

    def SetMaster(self, entity_id, game_master):
        self.game_master = game_master
        self.entity_id = entity_id

    def SetActive(self, active):
        assert hasattr(self, "game_master")
        if self.active == active:
            return

        self.active = active
        self.OnActive(active)

    def OnActive(self, active):
        pass


class GameMaster(NeptuneServiceSkeleton):
    def __init__(self, frame_rate, name='Game'):
        super().__init__(name)
        self.frame_rate = frame_rate
        self.frame_delta = 1 / frame_rate
        self.frame = 0
        # self.entities = DoubleLinkedList()
        self.entities = {}
        # self.eid_to_nodes = {}
        self._entity_id = 0

    def NewEntityId(self):
        eid = self._entity_id
        self._entity_id += 1
        return eid

    def AddEntity(self, entity: NeptuneGameEntity):
        eid = self.NewEntityId()
        entity.SetMaster(eid, self)
        # self.eid_to_nodes[eid] = self.entities.Add(eid, entity)
        self.entities[eid] = entity

    def RemoveEntity(self, entity: NeptuneGameEntity):
        # node = self.eid_to_nodes.pop(entity.entity_id, None)
        # if node is not None:
        #     self.entities.Delete(node)
        self.entities.pop(entity.entity_id, None)

    def Init(self):
        pass

    def Update(self, time_delta):
        for entity in self.entities.values():
            if entity.active:
                try:
                    entity.Update(time_delta)
                except Exception as e:
                    self.get_logger().error(traceback.format_exc())

    def LateUpdate(self, time_delta):
        for entity in self.entities.values():
            if entity.active:
                try:
                    entity.LateUpdate(time_delta)
                except Exception as e:
                    self.get_logger().error(traceback.format_exc())

    def FixedUpdate(self):
        self.frame += 1
        for entity in self.entities.values():
            if entity.active:
                try:
                    entity.FixedUpdate()
                except Exception as e:
                    self.get_logger().error(traceback.format_exc())

    async def logic(self):
        last_frame_time = time.time()
        time_delta_acum = 0
        while True:
            now = time.time()
            time_delta_acum += now - last_frame_time

            if time_delta_acum < self.frame_delta:
                last_frame_time = now
                await asyncio.sleep(self.frame_delta - time_delta_acum)
                continue

            while time_delta_acum >= self.frame_delta:
                self.FixedUpdate()
                time_delta_acum -= self.frame_delta

            self.Update(now - last_frame_time)
            self.LateUpdate(now - last_frame_time)
            last_frame_time = now
            # give other coroutine a chance to run
            # otherwise when time_delta_acum is always greater than self.frame_delta
            # (i.e. when the game logic is too slow to catch up with frame rate)
            # it will block the whole async loop
            await asyncio.sleep(0)
            self.get_logger().info(f"frame {self.frame} delta: {time.time() - now}")

    async def finish(self):
        pass


if __name__ == '__main__':
    import random
    dl = DoubleLinkedList()
    dllist = []
    for i in range(10):
        dllist += [dl.Add(i, i)]

    random.shuffle(dllist)
    for node in dllist[5:]:
        dl.Delete(node)
    dl.Add(13, 13)
    dl.Add(13, 13)
    dl.Delete(dl.Add(13, 13))
    print(dl)
