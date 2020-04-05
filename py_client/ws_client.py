import websockets
import asyncio
import base64
import json


async def client():
    uri = "ws://localhost:9090/neptune"
    try:
        async with websockets.connect(uri) as ws:
            while True:
                await ws.send("hello")
                await ws.send("world")
                msg = await ws.recv()
                result = json.loads(msg)
                print(result)

    except KeyboardInterrupt:
        ws.close()

asyncio.get_event_loop().run_until_complete(client())
