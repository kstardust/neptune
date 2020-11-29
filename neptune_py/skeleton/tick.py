import time
import collections
import math
from neptune_py.skeleton.game import DoubleLinkedList
import logging, traceback


CalloutNode = collections.namedtuple('CalloutNode', ['frame', 'interval', 'callback', 'callback_args'])


class NeptuneTick:

    def __init__(self, frame_rate=60, callout_queue_size=200):
        self.frame_rate = frame_rate
        self.frame_delta = 1.0 / frame_rate
        self.callout_queue_size = callout_queue_size
        self.frame = 0
        self.callout_queue = [DoubleLinkedList() for _ in range(self.callout_queue_size)]

        self.callout_data = {}

        self.callout_id = 0

    def get_logger(self):
        return logging.getLogger('NeptuneTick')

    def Update(self):
        self.frame += 1
        callout_list = self.callout_queue[self.frame % self.callout_queue_size]
        for node in callout_list:
            callout_id, schedule_frame = node.key, node.value
            if schedule_frame == self.frame:
                try:
                    callout, node = self.callout_data.pop(callout_id, (None, None))
                    callout_list.Delete(node)
                    callout.callback(*callout.callback_args)
                except Exception as e:
                    self.get_logger().error(traceback.format_exc())

                if callout.interval > 0:
                    self._Invoke(callout_id, callout.interval, callout.interval, callout.callback, callout.callback_args)

    def _Invoke(self, callout_id, delay_frames, interval_frames, func, args):
        schedule_frame = max(1, delay_frames) + self.frame
        callout_list = self.callout_queue[schedule_frame % self.callout_queue_size]
        self.callout_data[callout_id] = \
            CalloutNode(schedule_frame, interval_frames, func, args or []), callout_list.Add(callout_id, schedule_frame)

    def InvokeOnce(self, delay, func, *args):
        delay = max(0, delay)
        frames = math.ceil(delay * self.frame_rate)
        callout_id = self.callout_id
        self.callout_id += 1
        self._Invoke(callout_id, frames, 0, func, args)
        return callout_id

    def InvokeRepeat(self, delay, interval, func, *args):
        delay = max(0, delay)
        delay_frames = math.ceil(delay * self.frame_rate)
        interval_frames = math.ceil(interval * self.frame_rate)
        callout_id = self.callout_id
        self.callout_id += 1
        self._Invoke(callout_id, delay_frames, interval_frames, func, args)
        return callout_id

    def CancelTick(self, callout_id):
        _, node = self.callout_data.pop(callout_id, (None, None))
        if node:
            callout_list = self.callout_queue[node.value % self.callout_queue_size]
            callout_list.Delete(node)


if __name__ == "__main__":

    tick = NeptuneTick()
    rid = tick.InvokeRepeat(3, 0.5, lambda x: print(x), 1)

    for i in range(200):
        tick.InvokeOnce(i/10, lambda x: print(x), i)

    while True:
        tick.Update()
        time.sleep(1/60)
