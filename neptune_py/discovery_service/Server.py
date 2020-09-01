import logging


class NeptuneServiceClient:
    def __init__(self, channel):
        self.services = {}
        self._channel = channel

    def add_service(self):
        pass


class NeptuneService:
    def __init__(self, name, server):
        self.name = name

    def add_to_server(self, server):
        raise NotImplementedError("this method add service to grpc server")


class NeptuneServer:
    def __init__(self):
        self.service_s = set()
        self.service_c = set()
        self.channels = set()

    def register_service_s(self, service):
        print(f'register service {service}')
        self.service_s.add(service)

    def register_service_c(self, service):
        pass

    async def run(self, logic):
        try:
            await logic(self)
        except Exception as e:
            print(e)
        finally:
            print('stop running')

    def serve(self, server):
        for service in self.service_s:
            service.add_to_server(server)
