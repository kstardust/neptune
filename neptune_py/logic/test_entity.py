from neptune_py.skeleton.entity import NeptuneEntityBase
import aiohttp
import asyncio


class TestingClientEntity(NeptuneEntityBase):
    async def HttpFetchPoem(self, callback):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://v1.jinrishici.com/rensheng.txt") as resp:
                if resp.status == 200:
                    callback(await resp.text())
                else:
                    callback('failed')

    def Rpc2ServerReqEcho(self, arg):
        print(f'RpcReqTestEcho, {arg}')
        self.rpc_stub.Rpc2ClientRespEcho(arg)

    def Rpc2ServerReqGetPoem(self):
        print(f'RpcReqGetPoem')
        asyncio.create_task(self.HttpFetchPoem(self.rpc_stub.Rpc2ClientRespShowPoem))
