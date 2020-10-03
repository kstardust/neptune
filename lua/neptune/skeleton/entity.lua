local exports = {}

local common = require("neptune.skeleton.common")

local NeptuneEntityBase = common.Class.new('NeptuneEntityBase')
NeptuneEntityBase.__index = NeptuneEntityBase
function NeptuneEntityBase:ctor()
   return setmetatable({}, self)
end

exports.NeptuneEntityBase = NeptuneEntityBase
return exports
