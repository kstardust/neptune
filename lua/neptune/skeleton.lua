local exports = {}

local cocos_ws_rpc = require("neptune.cocos_ws_rpc")
local entity = require("neptune.skeleton.entity")
local remote_call = require("neptune.skeleton.remote_call")


local TestingEntity = setmetatable({}, {__index = entity.NeptuneEntityBase})
TestingEntity.__index = TestingEntity
function TestingEntity:Init()
   local ws_rpc = cocos_ws_rpc.NeptuneWSRpc:ctor("ws://echo.websocket.org")

   self.rpc = remote_call.NeptuneRpcProxy:ctor(
      self,
      function(...) self.RpcEstablished(self, ...) end,
      function(...) self.RpcLost(self, ...) end
   )
   self.rpc:EstablishRpc(ws_rpc)
end

function TestingEntity:RpcEstablished()
   self.rpc.rpc_stub.NestedCall1('13').FinalCall(13)
end

function TestingEntity:RpcLost()
   print('---------lost rpc')
end

function TestingEntity:NestedCall1(arg)
   print('---------Nestedcall1', arg)
   return {FinalCall = function(self, arg) print(arg) end}
end

function exports.Init()
   print('stardustk13')
   local testingEntity = TestingEntity:ctor()
   testingEntity:Init()
end
   
return exports
