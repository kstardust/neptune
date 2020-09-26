-- Don't perform consercutive calls (i.e. perform two
-- remote call without consume the call_chain), otherwise
-- the later call will override the former call_chain if
-- they are from a common parent node, cause all sub nodes
-- share the same call_chain in parent node.

-- This will be improved in future version.


local function starts_with(str, start)
   return str:sub(1, #start) == start
end


NeptuneNestedRpcStub = {}
function NeptuneNestedRpcStub.__index(self, func_name)
   print('unknown method, create new call node, name: ', func_name)
   table.insert(self._call_chain, {func_name})
   rawset(self, func_name, NeptuneNestedRpcStub:New(nil, self))
   table.remove(self._call_chain)
   return rawget(self, func_name)
end


function NeptuneNestedRpcStub.__call(self, ...)
   if #self._call_chain == 0 then
      -- TODO: assert messager is not empty
      print('empty call chain')
      return
   end

   local current_call = self._call_chain[#self._call_chain]
   current_call[2] = {...}
   local func_name = table.unpack(current_call)

   if starts_with(func_name, 'Nested') then
      return self
   else
      -- actually perform call
      for k, v in ipairs(self._call_chain) do
	 print('chained call----------', k)
	 print('-func name', v[1])
	 for k1, v1 in ipairs(v[2]) do
	    print('-arg', k1, v1)
	 end
      end
      --- test fake message
      return self._call_chain
   end
end


function NeptuneNestedRpcStub:New(messager, parent)
   local t = {}
   setmetatable(t, self)
   t._call_chain = {}
   if parent ~= nil then
      t.messager = parent.messager
      -- Do we really need to copy call_chain ?
      t._call_chain = {table.unpack(parent._call_chain)}
   else
      t.messager = messager
   end

   if t.messager == nil then
      -- TODO: assert messager is not nil here
      print('messager cannot be nil')
   end

   return t
end


NeptuneNestedRpc = {}
function NeptuneNestedRpc:execute(call_chain)
   local slot = self.entity
   for i, call in ipairs(call_chain) do
      local func_name, args = table.unpack(call)
      print(i, func_name, table.unpack(args))
      slot = slot[func_name](table.unpack(args))
   end
end

function NeptuneNestedRpc:New(entity)
   local t = {}
   setmetatable(t, self)
   self.__index = self
   t.entity = entity
   return t
end

------------------------- Test Code
function NestedCall2(...)
      print('NestedCall2', ...)
      return { NestedCall3 = NestedCall3, NestedCall4 = NestedCall4 }
end

function NestedCall3(...)
      print('NestedCall3', ...)
      return { FinalCall = FinalCall }
end

function NestedCall4(...)
      print('NestedCall4', ...)
      return { FinalCall = FinalCall }
end

function FinalCall(...)
      print('FinalCall', ...)
end

fake_entity = {
   NestedCall1 = function (...)
      print('NestedCall1', ...)
      return { NestedCall2 = NestedCall2 }
   end
}

stub = NeptuneNestedRpcStub:New(13)
slot = NeptuneNestedRpc:New(fake_entity)
-- dont call stub method with `:`,  the colon operator
-- has an extra self parameter.
message = stub.NestedCall1(13, 13).NestedCall2(13, 13).NestedCall3(13, 13).FinalCall(13, 13)
slot:execute(message)

message = stub.NestedCall1(1, 13).NestedCall2(1, 13).NestedCall4(13, 13).FinalCall(13, 1)
slot:execute(message)
