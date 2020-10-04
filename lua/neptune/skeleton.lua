local exports = {}

local cocos_ws_rpc = require("neptune.cocos_ws_rpc")
local entity = require("neptune.skeleton.entity")
local remote_call = require("neptune.skeleton.remote_call")


local TestingEntity = setmetatable({}, {__index = entity.NeptuneEntityBase})
TestingEntity.__index = TestingEntity
function TestingEntity:Init(label)

   self.label = label
   -- 创建 websocket rpc 连接器，负责网络数据传输
   local ws_rpc = cocos_ws_rpc.NeptuneWSRpc:ctor("ws://127.0.0.1:1313/13")

   -- 创建 rpc proxy
   self.rpc = remote_call.NeptuneRpcProxy:ctor(
      self,                                             -- rpc 绑定的实体，远端发回的 rpc 会在这个对象上执行
      function(...) self.RpcEstablished(self, ...) end, -- rpc 连接建立成功的回调
      function(...) self.RpcLost(self, ...) end,         -- rpc 连接断开的回调
      function(...) self.RpcError(self, ...) end        -- rpc 连接错误的回调
   )

   -- 利用 websocket 来连接到远端
   self.rpc:EstablishRpc(ws_rpc)
end

function TestingEntity:RpcEstablished()
   local arg = {
      ["13"] = 13
   }
   self.rpc.rpc_stub.Rpc2ServerReqEcho(arg)
end

function TestingEntity:RpcLost()
   print('---------lost rpc')
end

function TestingEntity:RpcError(err)
   print('---------rpc error', err)
end

function TestingEntity:Rpc2ClientRespEcho(arg)
   print('---------Rpc2ClientRespEcho', arg)
end

function TestingEntity:Rpc2ClientRespShowPoem(poem)
   self.label:setString(poem)
end

function exports.GetTestingEntity(label)
   local testingEntity = TestingEntity:ctor()
   testingEntity:Init(label)
   return testingEntity
end
   
return exports
