import uuid
import logging
import asyncio


class NeptuneService:
    def __init__(self, server, name=None):
        self.name = uuid.uuid4() if name is None else name
        self.server = server
        self._inited = False
        self._logic_task = None

    def init(self):
        """
        init service
        """
        if self._inited:
            return

        self._inited = True
        print(f"init service {self.name}")

    async def logic(self):
        """
        service logic
        """
        print(f"logic fun {self.name}")
        await asyncio.sleep(10)
        pass

    async def finished(self):
        """
        service finished
        """
        print(f"finished fun {self.name}")
        pass

    async def run(self):
        self.init()
        try:
            self._logic_task = asyncio.wait_for(self.logic(), None)
            await self._logic_task
        except Exception as e:
            if isinstance(e, asyncio.CancelledError):
                print(f'service {self.name} was cancelled')
            else:
                raise e
        finally:
            await self.finished()
            print(f'service {self.name} finished')

    def stop(self):
        if self._logic_task is not None and self._logic_task.done():
            self._logic_task.cancel()


class NeptuneServer:
    def __init__(self):
        self.services = set()

    def add_service(self, service: NeptuneService):
        self.services.add(service)

    def init():
        pass

    async def run(self):
        for service in self.services:
            service.init()

        ret = await asyncio.gather(
            *(service.run() for service in self.services),
            return_exceptions=True
        )
        print(ret)

async def main():
    server = NeptuneServer()
    server.add_service(NeptuneService(server))
    server.add_service(NeptuneService(server))
    await server.run()

asyncio.run(main())
