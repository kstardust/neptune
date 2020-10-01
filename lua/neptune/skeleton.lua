local Neptune = {}

local wstest = require("neptune.websocket_rpc")
local rpc = require("neptune.skeleton.remote_call")

local XXXEntity = {}
XXXEntity.__index = function(self, func_name)
   print('XXXEntity', func_name)
   return self
   end

XXXEntity.__call = function(self, ...)
   print('XXXEntity', ...)
   return self
   end

setmetatable(XXXEntity, XXXEntity)

function Neptune.Init()
   print('stardustk13')
   local ws = wstest.NeptuneWSRpc:ctor({})
   ws:Connect("ws://echo.websocket.org")

   local buf = nil
   local sender = function (x)
      buf = x
   end
   print(rpc.NeptuneNestedRpcStub)
   local rpcstub = rpc.NeptuneNestedRpcStub:ctor(sender)
   rpcstub.NestedCall1(13).NestedCall1(13).FinalCall({13})
   local rpcs = rpc.NeptuneNestedRpc:ctor(XXXEntity)
   rpcs:Execute(buf)
end
   
return Neptune
