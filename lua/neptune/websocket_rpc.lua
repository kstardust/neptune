-- cocos2dx documentation is a nightmare,
-- I doubt if anyone can figure out how to use cocos2dx ws api just by reading this doc.
-- https://docs.cocos2d-x.org/api-ref/cplusplus/v3x/d0/dab/classcocos2d_1_1network_1_1_web_socket.html
-- anyway found a simple usage here: https://gameinstitute.qq.com/community/detail/101143

local common = require("neptune.skeleton.common")
local exports = {}

local NeptuneWSRpc = common.Class.new("NeptuneWSRpc")
NeptuneWSRpc.__index = NeptuneWSRpc
function NeptuneWSRpc:ctor(messager_cls)
   local o = setmetatable({
         messager_cls = messager_cls
      },
      self
   )
   return o   
end

function NeptuneWSRpc:Connect(address)
   if self.ws ~= nil then
      error('already opened')
   end
   local ws = cc.WebSocket:create(address)
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
   print('opened', self, self.ws)
   self.ws:sendString('love13')
end

function NeptuneWSRpc:OnMessage(...)
   print('recv', ...)
   self.ws:close()
end

function NeptuneWSRpc:OnClose(...)
   print('close', ...)
end

function NeptuneWSRpc:OnError(...)
   print('erro', ...)
end

exports.NeptuneWSRpc = NeptuneWSRpc
return exports
