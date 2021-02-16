// Learn TypeScript:
//  - https://docs.cocos.com/creator/manual/en/scripting/typescript.html
// Learn Attribute:
//  - https://docs.cocos.com/creator/manual/en/scripting/reference/attributes.html
// Learn life-cycle callbacks:
//  - https://docs.cocos.com/creator/manual/en/scripting/life-cycle-callbacks.html

export interface INeptuneMessager {
    SendMessage(message: string);
    OnConnected(event);
    OnClose(event);
    OnError(event);
    OnMessage(event);
}

export interface INeptuneNetEntity {
    OnConnected();
    OnClose();
    OnError();
    OnMessage(msg: string);
    BindMessager(messager: INeptuneMessager);
}
