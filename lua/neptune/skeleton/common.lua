local common = {}

local Class = {}
Class.__index = Class
function Class.new(type_)
   local self = setmetatable({
         type = type_
   }, Class)
   return self
end

common.Class = Class
return common
