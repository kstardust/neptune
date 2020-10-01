local common = require("neptune.skeleton.common")

local NeptuneSkeleton = {}

local NeptuneEntityBase = common.Class.new('NeptuneEntityBase')
NeptuneEntityBase.__index = NeptuneEntityBase


local NeptuneRemoteEntity = NeptuneEntityBase:ctor()
