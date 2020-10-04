-- Don't perform consercutive calls (i.e. perform two
-- remote call without consume the call_chain), otherwise
-- the later call will override the former call_chain if
-- they are from a common parent node, cause all sub nodes
-- share the same call_chain in parent node.

-- This will be improved in future version.
local exports = {}

local json = require("neptune.utils.json")
local np_messager = require("neptune.skeleton.messager")
local common = require("neptune.skeleton.common")


local function starts_with(str, start)
   return str:sub(1, #start) == start
end


local NeptuneNestedRpcStub = {}
function NeptuneNestedRpcStub.__index(self, func_name)
   print('unknown method, create new call node, name: ', func_name)
   table.insert(self._call_chain, {func_name})
   rawset(self, func_name, NeptuneNestedRpcStub:ctor(nil, nil, self))
   table.remove(self._call_chain)
   return rawget(self, func_name)
end


function NeptuneNestedRpcStub.__call(self, ...)
   if #self._call_chain == 0 then
      error('empty call chain')
      return
   end

   local current_call = self._call_chain[#self._call_chain]
   current_call[2] = {...}
   local func_name = common.unpack(current_call)

   if starts_with(func_name, 'Nested') then
      return self
   else
      -- 本来想抽出来，self.PerformRpc，
      -- 结果因为 __index 已经被设置为了函数，
      -- 而 Lua OOP 需要把 __index 设为 class
      -- 的 table(不然找不到类方法)
      self.sender(self.encoder(self._call_chain))      
   end
end


function NeptuneNestedRpcStub:ctor(sender, encoder, parent)
   local t = {}
   setmetatable(t, self)
   t._call_chain = {}
   if parent ~= nil then
      t.sender = parent.sender
      t.encoder = parent.encoder
      t._call_chain = {common.unpack(parent._call_chain)}
   else
      t.sender = sender
      t.encoder = encoder
   end

   if rawget(t, 'sender') == nil then
      error('sender cannot be nil')
   end

   if rawget(t, 'encoder') == nil then
      t.encoder = json.encode
   end
   
   return t
end


local NeptuneNestedRpc = {}
NeptuneNestedRpc.__index = NeptuneNestedRpc
function NeptuneNestedRpc:ctor(entity, decoder)
   local o = setmetatable({
         decoder = decoder or json.decode,
         entity = entity
      },
      self
   )
   return o
end

function NeptuneNestedRpc:Execute(call_chain_data)
   local call_chain = self.decoder(call_chain_data)
   local slot = self.entity
   for i, call in ipairs(call_chain) do
      local func_name, args = common.unpack(call)
      slot = slot[func_name](slot, common.unpack(args))
   end
end

local NeptuneRpcProxy = {}
NeptuneRpcProxy.__index = NeptuneRpcProxy
function NeptuneRpcProxy:ctor(entity, established_callback, lost_callback, error_callback)
   local o = setmetatable({
         entity = entity,
         established_callback = established_callback,
         lost_callback = lost_callback,
         error_callback = error_callback
   }, self)
   o.rpc_executor = NeptuneNestedRpc:ctor(o.entity)
   return o
end

function NeptuneRpcProxy:EstablishRpc(connector)
   connector:Connect(
      function (writer)
         return np_messager.NeptuneMessager:ctor(writer, self)
      end
   )
end

function NeptuneRpcProxy:BindMessager(messager)
   print('RpcProxy Bind Messager')
   self.messager = messager
   self.rpc_stub = NeptuneNestedRpcStub:ctor(
      function (msg)
         self.messager:WriteMessage(
            np_messager.NeptuneMessageType.NeptuneMessageTypeCall,
            msg
         )
      end
   )
   if self.established_callback ~= nil then
      self.established_callback()      
   end   
end

function NeptuneRpcProxy:OnMessagerLost()
   if self.lost_callback ~= nil then
      self.lost_callback()
   end
end

function NeptuneRpcProxy:Close()
   self.messager:Close()
end

function NeptuneRpcProxy:OnError(err)
   if self.error_callback ~= nil then
      self.error_callback(err)
   end
end

function NeptuneRpcProxy:OnMessage(mtype, msg)
   print(mtype, msg)
   if mtype == np_messager.NeptuneMessageType.NeptuneMessageTypeCall then
      self.rpc_executor:Execute(msg)
   else
      print('unknown message type', mtype, msg)
   end
end

exports.NeptuneRpcProxy = NeptuneRpcProxy
exports.NeptuneNestedRpc = NeptuneNestedRpc
exports.NeptuneNestedRpcStub = NeptuneNestedRpcStub

return exports
