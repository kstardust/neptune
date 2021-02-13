import asyncio
from . router_server import NeptuneRouter


if __name__ == '__main__':
    np = NeptuneRouter('router_13')
    asyncio.run(np.run())
