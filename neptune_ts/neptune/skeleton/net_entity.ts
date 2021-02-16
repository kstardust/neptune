// Learn TypeScript:
//  - https://docs.cocos.com/creator/manual/en/scripting/typescript.html
// Learn Attribute:
//  - https://docs.cocos.com/creator/manual/en/scripting/reference/attributes.html
// Learn life-cycle callbacks:
//  - https://docs.cocos.com/creator/manual/en/scripting/life-cycle-callbacks.html

import { INeptuneNetEntity, INeptuneMessager } from "./interfaces";
import { NeptuneRpcExecutor, NeptuneRpcStub } from "./remote_call";

export class NetEntityBase implements INeptuneNetEntity {
    public messager: INeptuneMessager;
    constructor() {
    }

    OnError() {
        this.messager = null;
    }

    OnConnected() {
        console.log("entity connected");
    }

    OnMessage(msg: string) {
    }

    OnClose() {
        this.messager = null;
    }

    BindMessager(messager: INeptuneMessager) {
        this.messager = messager;
    }
}


export class NeptuneRpcEntityBase extends NetEntityBase {
    rpcExecutor: NeptuneRpcExecutor;
    private rpcStub: any;

    constructor() {
        super();
        this.rpcExecutor = new NeptuneRpcExecutor(this);
    }

    SetRpcStub(rpcStub: any) {
        this.rpcStub = rpcStub;
    }

    OnMessage(msg: string) {
        if (this.rpcExecutor == null) {
            console.error("entity doesnt have a rpc executor");
            return;
        }
        this.rpcExecutor.Execute(msg);
    }

    BindMessager(messager: INeptuneMessager) {
        super.BindMessager(messager);
        this.rpcStub.SetMessager(messager);
    }
}
