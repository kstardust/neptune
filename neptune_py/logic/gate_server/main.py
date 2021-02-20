import asyncio
from .ws_gate_server import NeptuneWebsocketGateServer


if __name__ == "__main__":
    np = NeptuneWebsocketGateServer("13:gate1:")
    asyncio.run(np.run())
