import asyncio
from .ws_gate_server import NeptuneWebsocketGateServer


if __name__ == "__main__":
    np = NeptuneWebsocketGateServer("NeptuneWebsocketGateServer")
    asyncio.run(np.run())
