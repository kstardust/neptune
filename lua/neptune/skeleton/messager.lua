local common = require("neptune.skeleton.common")

local NeptuneSkeleton = {}

local NeptuneMessageType = common.Constant({
   NeptuneMessageTypeCall = 1
})

local NeptuneMessager = common.Class.new('NeptuneMessager')
NeptuneMessager.__index = NeptuneMessager
function NeptuneMessager:ctor(read_writer, entity_cls)
   local o = setmetatable({
         read_writer = read_writer,
         entity_cls = entity_cls,
      },
      self
   )
   return o
end

function NeptuneMessager:OnConnected()
   if self.entity ~= nil then
      error("this messager already has entity?")
   end
   self.entity = self.entity_cls()
   self.entity:BindMessager(self)
end

function NeptuneMessager:OnMessage(mtype, msg)
   if self.entity ~= nil then
      error("this messager doesnt have entity")
   end
   self.entity = self.entity_cls()
   self.entity:BindMessager(self)
end

function NeptuneMessager:OnError(err)
   print("not implemented")
end

function NeptuneMessager:OnDisconnected()
   self.entity:OnMessagerLost()
end

function NeptuneMessager:Close()
   print("not implemented")
end

function NeptuneMessager:SendMessage(mtype, msg)
   self.read_writer.WriteMessage(mtype, msg)
end


-- local NeptuneMessagerClientManager = common.Class.new('NeptuneMessagerClientManager')
-- NeptuneMessagerClientManager.__index = NeptuneMessagerClientManager
-- function NeptuneMessagerClientManager:ctor(entity_cls)
--    local o = setmetatable({
--          entity_cls = entity_cls
--          messagers = {}
--       },
--       self
--    )
--    return o
-- end

-- function NeptuneMessagerClientManager:OnConnected(id, read_writer)
--    self.messagers[id] = NeptuneMessager:ctor(id, self, read_writer)
--    self.messagers[id].OnConnected()
-- end

-- function NeptuneMessagerClientManager:OnMessage(id, mtype, msg)
--    local messager = self.messagers[id]
--    if messager == nil then
--       error('unknown message id=' .. id)
--    end
--    messager.OnMessage(id, mtype, msg)
-- end

-- function NeptuneMessagerClientManager:OnDisconnected(id)
--    local messager = self.messagers[id]
--    if messager == nil then
--       error('unknown message id=' .. id)
--    end
--    messager.OnDisconnected()
--    self.messagers[id] = nil
-- end

-- function NeptuneMessagerClientManager:OnError(id, err)
--    local messager = self.messagers[id]
--    if messager == nil then
--       error('unknown message id=' .. id)
--    end
--    messager.OnError(err)
--    self.messagers[id] = nil   
-- end


-- export
NeptuneSkeleton.NeptuneMessager = NeptuneMessager
-- NeptuneSkeleton.NeptuneMessagerClientManager = NeptuneMessagerClientManager

return NeptuneSkeleton
