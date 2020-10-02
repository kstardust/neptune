local common = {}

local Class = {}
Class.__index = Class
function Class.new(type_)
   local self = setmetatable({
         type = type_
   }, Class)
   return self
end

function Constant(o)
   return setmetatable({}, {
         __index = o,
         __newindex = function(t, k, v)
            error('const is read-only')
         end,
         __metatable = false
   })
end

common.Class = Class
return common
