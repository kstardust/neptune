import asyncio
from . router_manager import NeptuneRouterManagerApp


if __name__ == '__main__':
    router_manager = NeptuneRouterManagerApp("router_manager")
    asyncio.run(router_manager.run())
