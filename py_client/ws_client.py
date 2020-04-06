import websockets
import asyncio
import base64
import json
import requests
import sys

#resp = requests.get("http://localhost:9090/new", params={'ships':2, 'fps':1})
#resp = resp.json()
#print(resp)
#did = resp['dock']
#print(did)

async def client(did):
#   uri = "ws://192.168.12.138:11111/neptune"
    uri = "ws://localhost:9090/neptune"
    try:
        async with websockets.connect(uri) as ws:
            while True:
                await ws.send(did)
                await ws.send("world")
                msg = await ws.recv()
                result = json.loads(msg)
                print(result)

    except KeyboardInterrupt:
        ws.close()


asyncio.get_event_loop().run_until_complete(client(sys.argv[1]))

# 20 fps 向所有连接的客户端推送数据：
# {
#     'Frame': 9067,  # 第几帧
#     'Containers':   # 这一帧收到的数据（数组，时间排序）
#     [
#         {'Id': 185,               # 数据唯一 ID
#          'Time': 9670444,         # 该数据于此帧的开始后的多久收到，纳秒，比如这个是第 9076 帧的第 9.6ms 收到
#          'Payload': 'aGVsbG8='    # 客户端上发的数据，要用 base64 解码，比如这个其实是字符串 'hello'
#         },
#         {'Id': 186,
#          'Time': 9673797,
#          'Payload': 'd29ybGQ='}
#     ]
# }
