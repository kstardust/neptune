from logf import logger


class PeerAbstract(object):
    def __init__(self, r, w, bk_size=4096):
        self.reader = r
        self.writer = w
        self.bk_size = bk_size
        self.should_close = False

    async def on_connect(self):
        raise NotImplementedError

    async def on_close(self):
        raise NotImplementedError

    async def on_input(self, data):
        raise NotImplementedError

    async def send(self, data):
        self.writer.write(data)
        await self.writer.drain()

    async def serve(self):
        await self.on_connect()

        while True:
            data = None
            if not self.should_close:
                try:
                    data = await self.reader.read(self.bk_size)
                except ConnectionResetError:
                    logger.info("reset by peer")
                    self.should_close = True
            if self.should_close or not data:
                await self.on_close()
                self.writer.close()
                if not self.should_close:
                    await self.writer.wait_closed()
                return

            await self.on_input(data)


class SEPeerEchoDummy(PeerAbstract):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self._socket = self.writer.get_extra_info('socket')

    async def on_connect(self):
        logger.info("connected: {}".format(self._socket.getpeername()))

    async def on_close(self):
        logger.info("closed: {}".format(self._socket.getpeername()))

    async def on_input(self, data):
        await self.send(data)
