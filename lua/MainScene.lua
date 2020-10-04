
local MainScene = class("MainScene", cc.load("mvc").ViewBase)
local neptune = require("neptune.skeleton")
   
function MainScene:onCreate()
    -- add background image
    -- display.newSprite("HelloWorld.png")
    --     :move(display.center)
    --     :addTo(self)

    -- add HelloWorld label
    local label = cc.Label:createWithSystemFont("Hello World", "Arial", 40)
        :move(display.cx, display.cy + 200)
       :addTo(self)

    local entity = neptune.GetTestingEntity(label)

    local button = ccui.Button:create()

    button:addClickEventListener(function(sender, type)
          entity.rpc.rpc_stub.Rpc2ServerReqGetPoem()
    end)
    button:move(display.center)
    button:setTitleText("Click")
    button:setTitleFontSize(28)
    button:setTitleColor(cc.c3b(0,255,255))
    button:addTo(self)
end

return MainScene
