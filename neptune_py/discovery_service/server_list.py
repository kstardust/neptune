from datetime import (datetime, timedelta)


class Server:
    def __init__(self, pid, data):
        self.pid = pid
        self.data = data
        self.last_seen = datetime.now()


class ServerList:
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
        self._peers[id_] = Server(pid=id_, data=data)
        return True

    def keepalive(self, id_):
        self.expire()
        if id_ not in self._peers:
            return False
        peer = self._peers[id_]
        peer.last_seen = datetime.now()
        return True

    @property
    def servers(self):
        self.expire()
        return [v.data for v in self._peers.values()]
