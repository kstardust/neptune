import uuid
import logging
import asyncio
import sys

G = None


class NeptuneServiceSkeleton:
    class ServiceStatus:
        NEW = 1
        INITED = 2
        RUNNING = 3
        FINISHED = 4

    def __init__(self, name=None):
        self.name = str(uuid.uuid4()) if name is None else name
        self._status = NeptuneServiceSkeleton.ServiceStatus.NEW
        self._logic_task = None

    def get_logger(self):
        return self.server.get_logger(self.name)

    def init_service(self, server):
        if self._status != NeptuneServiceSkeleton.ServiceStatus.NEW:
            return
        self._status = NeptuneServiceSkeleton.ServiceStatus.INITED
        self.server = server
        self.init()

    def init(self):
        """
        init service
        """
        self.get_logger().debug(f"init service {self.name}")

    async def logic(self):
        """
        service logic
        """
        self.server.get_logger().debug(f"logic fun {self.name}")
        await asyncio.sleep(10)

    async def finish_service(self):
        if self._status != NeptuneServiceSkeleton.ServiceStatus.RUNNING:
            self.server.get_logger().error(f"service {self.name} is not running")
            return
        else:
            await self.finish()

    async def finish(self):
        """
        service finished
        """
        self.server.get_logger().debug(f"finished fun {self.name}")

    async def run(self):
        assert self._status == NeptuneServiceSkeleton.ServiceStatus.INITED
        self._status = NeptuneServiceSkeleton.ServiceStatus.RUNNING
        try:
            self._logic_task = asyncio.create_task(self.logic())
            await self._logic_task
        except Exception as e:
            if isinstance(e, asyncio.CancelledError):
                self.server.get_logger().debug(f'service {self.name} was cancelled')
            else:
                raise e
        finally:
            await self.finish_service()
            self.server.get_logger().debug(f'service {self.name} finished')

    async def stop(self):
        if self._logic_task is not None and not self._logic_task.done():
            self._logic_task.cancel()


class NeptuneServerSkeleton:
    def __init__(self, server_name):
        global G
        assert G is None
        G = self

        self.services = {}
        self.server_name = server_name
        self._init_logger()

    def _init_logger(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(levelname)s][%(name)s %(asctime)s]:%(message)s"
        )

    def get_logger(self, name=None):
        return logging.getLogger(
            name if name is not None else self.server_name
        )

    def add_service(self, service: NeptuneServiceSkeleton):
        self.services[service.name] = service

    def init_services(self):
        for service in self.services.values():
            service.init_service(self)

    def find_service(self, service_name):
        return self.services.get(service_name)

    async def run(self):
        self.init_services()
        task = asyncio.gather(
            *(service.run() for service in self.services.values()),
        )
        ret = None
        try:
            ret = await task
        finally:
            task.cancel()
            self.get_logger().debug(f"gathered all task {ret}")
