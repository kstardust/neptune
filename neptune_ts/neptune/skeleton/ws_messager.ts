// Learn TypeScript:
//  - https://docs.cocos.com/creator/manual/en/scripting/typescript.html
// Learn Attribute:
//  - https://docs.cocos.com/creator/manual/en/scripting/reference/attributes.html
// Learn life-cycle callbacks:
//  - https://docs.cocos.com/creator/manual/en/scripting/life-cycle-callbacks.html

import {INeptuneMessager, INeptuneNetEntity} from "./interfaces";


export class NeptuneWSMessager implements INeptuneMessager {
    private url: string;
    private ws: WebSocket;

    constructor(public entity: INeptuneNetEntity) {
    }

    Connect(url: string) {
        this.url = url;
        this.ws = new WebSocket(url);
        // use arrow function to catch `this`
        this.ws.onopen = e => this.OnConnected(e);
        this.ws.onerror = e => this.OnError(e);
        this.ws.onmessage = e => this.OnMessage(e);
        this.ws.onclose = e => this.OnClose(e);
    }

    OnConnected(event) {
        console.info("ws messager connected to ", this.url);        
        this.entity.BindMessager(this);
        this.entity.OnConnected();
    }

    OnClose(event) {
        console.error("ws messager closed ", this.url);
        this.entity.OnClose();
    }

    OnMessage(event) {
        console.log("ws messager received ", this.url, event.data);
        this.entity.OnMessage(event.data);
    }

    OnError(event) {
        console.error("ws messager error ocurred ", event);
        this.entity.OnError();
    }

    SendMessage(msg: string) {
        if (this.ws.readyState !== WebSocket.OPEN) {
            console.error(`cannot send message ws status is: ${this.ws.readyState}`);
            return;
        }
        this.ws.send(msg);
    }
}
