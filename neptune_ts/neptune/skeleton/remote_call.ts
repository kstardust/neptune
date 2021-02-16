// Learn TypeScript:
//  - https://docs.cocos.com/creator/manual/en/scripting/typescript.html
// Learn Attribute:
//  - https://docs.cocos.com/creator/manual/en/scripting/reference/attributes.html
// Learn life-cycle callbacks:
//  - https://docs.cocos.com/creator/manual/en/scripting/life-cycle-callbacks.html

interface INeptuneRpcSender {
    SendMessage(data: string);
}

interface INeptuneRpcNode {
    Aggregate(): any[];
    Perform();
    stub: NeptuneRpcStub;
    call_chain: any[];
}

interface INeptuneRpcEncoder {
    (call_chain: any[]): string;
}

interface INeptuneRpcDecoder {
    (message: string): any[];
}

export function NeptuneRpc(...reserved: any[]) {
    return function (target: INeptuneRpcNode, methodName: string, descriptor: PropertyDescriptor) {
        return {
            value: function (this: any, ...args: any[]) {
                this.call_chain.push([methodName, args]);                
                // this is for nested rpc,  you 
                // shouldn't do anything inside rpc stub except returning another stub object.
                let result = descriptor.value.apply(this, args);
                console.debug(`rpc methodName ${methodName} args: ${args} return type: ${typeof result}`);
                return result;
            }
        }
    }
}

// rpc base node
export class NeptuneRpcStubNode implements INeptuneRpcNode {
    call_chain: any[] = [];

    constructor(public stub: NeptuneRpcStub, protected parent: INeptuneRpcNode=null) {
        if (parent !== null) {
            this.stub = parent.stub;
            this.call_chain = parent.call_chain;
        }
    }

    Aggregate(): any[] {
        return this.call_chain;
    }
    
    Perform() {
        this.stub.RemoteCall(this.Aggregate());
        // clear call chain, (notice that all node from a same ancestor share a same call chain)
        this.call_chain.splice(0, this.call_chain.length);
    }
}

// rpc executor
export class NeptuneRpcExecutor {
    constructor(public entity: any, public decoder: INeptuneRpcDecoder=JSON.parse) {}

    Execute(rpc_message: string) {
        let call_chain = this.decoder(rpc_message);

        let target = this.entity;
        for (let call_node of call_chain) {            
            let method: string = call_node[0];
            let args: any[] = call_node[1];                        
            target = target[method].apply(target, args);
        }
    }
}

// stub-class-based rpc stub
export abstract class NeptuneRpcStub {

    constructor(public messager: INeptuneRpcSender, public encoder: INeptuneRpcEncoder=JSON.stringify) {
        this.InitRpcStubs();
    }

    abstract InitRpcStubs(): void;

    SetMessager(messager: INeptuneRpcSender) {
        this.messager = messager;
    }

    RemoteCall(call_chain: any[]): string {
        if (this.messager == null) {
            console.error("cannot perform rpc, messager is null");
            return
        }
        let message = this.encoder(call_chain);
        console.debug("RemoteCall: ", message)
        this.messager.SendMessage(message);
        // for debug purpose
        return message;
    }
}

// string-based rpc stub
// example: np_rpc_stub.RemoteCall("TestLayer1Rpc", 13, "13", [1, 3]).RemoteCall("TestLayer2Rpc", 13).Perform();
export class NeptuneRpcStringStub {
    protected call_chain: any[] = [];

    constructor(
        public messager: INeptuneRpcSender,
        public encoder: INeptuneRpcEncoder=JSON.stringify,
        protected parent: NeptuneRpcStringStub=null) {
            if (parent != null) {
                this.encoder = parent.encoder;
                this.messager = parent.messager;
            }
        }

    SetMessager(messager: INeptuneRpcSender) {
        this.messager = messager;
    }

    RemoteCall(funcname: string, ...args: any[]): NeptuneRpcStringStub {
        this.call_chain.push([funcname, args]);
        let newNode = this.Clone();
        return newNode;
    }

    Clone(): NeptuneRpcStringStub {
        let rpcNode = new NeptuneRpcStringStub(null, null, this);
        rpcNode.call_chain = this.call_chain;
        return rpcNode;
    }

    EncodeCallChain(): string {
        return this.encoder(this.call_chain);
    }

    Perform(): string {
        let message = this.EncodeCallChain();
        this.call_chain.splice(0, this.call_chain.length);
        this.messager.SendMessage(message);
        console.log("perform call", message);
        return message;
    }
}
