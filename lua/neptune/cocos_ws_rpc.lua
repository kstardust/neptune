-- cocos2dx documentation is a nightmare,
-- I doubt if anyone can figure out how to use cocos2dx ws api just by reading their doc.
-- https://docs.cocos2d-x.org/api-ref/cplusplus/v3x/d0/dab/classcocos2d_1_1network_1_1_web_socket.html
-- Anyway found a simple usage here: https://gameinstitute.qq.com/community/detail/101143

local common = require("neptune.skeleton.common")
local exports = {}

local NeptuneWSRpcWriter = common.Class.new("NeptuneWSRpcWriter")
NeptuneWSRpcWriter.__index = NeptuneWSRpcWriter
function NeptuneWSRpcWriter:ctor(ws)
   local o = setmetatable({
         ws = ws
      },
      self
   )
   return o   
end

function NeptuneWSRpcWriter:WriteMessage(mtype, msg)
   self.ws:sendString(string.format("%02d%s", mtype, msg))
end

function NeptuneWSRpcWriter:Close()
   self.ws:close()
end


local NeptuneWSRpc = common.Class.new("NeptuneWSRpc")
NeptuneWSRpc.__index = NeptuneWSRpc
function NeptuneWSRpc:ctor(address)
   local o = setmetatable({
         address = address
      },
      self
   )
   return o
end

function NeptuneWSRpc:Connect(messager_ctor)
   if self.ws ~= nil then
      error('already opened')
   end
   self.messager_ctor = messager_ctor

   local ws = cc.WebSocket:create(self.address)
   if ws ~= nil then
      self.ws = ws      
      ws:registerScriptHandler(function(...) self.OnOpened(self, ...) end, cc.WEBSOCKET_OPEN)
      ws:registerScriptHandler(function(...) self.OnMessage(self, ...) end, cc.WEBSOCKET_MESSAGE)
      ws:registerScriptHandler(function(...) self.OnClose(self, ...) end, cc.WEBSOCKET_CLOSE)
      ws:registerScriptHandler(function(...) self.OnError(self, ...) end, cc.WEBSOCKET_ERROR)
   else
      error('ws is nil')
   end
end

function NeptuneWSRpc:OnOpened()
   self.messager = self.messager_ctor(NeptuneWSRpcWriter:ctor(self.ws))
   self.messager:OnConnected()
   print('opened', self, self.ws)
end

function NeptuneWSRpc:OnMessage(data)
   print('recv', data)
   local mtype = tonumber(string.sub(data, 1, 2))
   local data  = string.sub(data, 3)
   self.messager:OnMessage(mtype, data)
end

function NeptuneWSRpc:OnClose(...)
   if self.messager ~= nil then
      self.messager:OnDisconnected()
   end
   print('close', ...)
end

function NeptuneWSRpc:OnError(err)
   if self.messager == nil then
      self.messager = self.messager_ctor(NeptuneWSRpcWriter:ctor(nil))      
   end
   self.messager:OnError(err)
end


exports.NeptuneWSRpcWriter = NeptuneWSRpcWriter
exports.NeptuneWSRpc = NeptuneWSRpc
return exports
