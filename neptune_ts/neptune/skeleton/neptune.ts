import { NeptuneRpc, NeptuneRpcStringStub, NeptuneRpcExecutor, NeptuneRpcStubNode, NeptuneRpcStub } from "./remote_call";
import { NeptuneWSMessager } from "./ws_messager";
import { NeptuneRpcEntityBase } from "./net_entity"


class BarRpcStub extends NeptuneRpcStubNode {
    @NeptuneRpc()
    NestedRpc(z: number[]): NeptuneRpcStubNode {
        return new NeptuneRpcStubNode(null, this);
    }
}

class GameServerPlayerStub extends NeptuneRpcStubNode {
    @NeptuneRpc()
    GameServerPlayerFooBarRpc(a: number) {
        return new NeptuneRpcStubNode(null, this);
    }
}

class ServerRpcStub extends NeptuneRpcStubNode {
    @NeptuneRpc()
    GetBar(): BarRpcStub {
        return new BarRpcStub(null, this);
    }

    @NeptuneRpc()
    TestRpc(a: number, b: string): NeptuneRpcStubNode { 
        return new NeptuneRpcStubNode(null, this); 
    }

    @NeptuneRpc()
    Login(token: string) { 
        return new NeptuneRpcStubNode(null, this); 
    }

    @NeptuneRpc()
    GetGameServerPlayer() {
        return new GameServerPlayerStub(null, this);
    }

}

class MyNeptuneRpcStub extends NeptuneRpcStub {
    // add root stub declarations at here
    ServerRpc: ServerRpcStub;
    MirrorRpc: MirrorClientRpc;

    InitRpcStubs() {
        // create root stubs at here
        this.ServerRpc = new ServerRpcStub(this);
        this.MirrorRpc = new MirrorClientRpc(this);
    }
}

class MirrorClientRpc extends NeptuneRpcStubNode {
    @NeptuneRpc()
    TestRpc(a: number, b: string) {
        return new NeptuneRpcStubNode(null, this);
    }

    @NeptuneRpc()
    GetLayer2(): MirrorClientRpcLayer2 {
        return new MirrorClientRpcLayer2(null, this);
    }
}

class MirrorClientRpcLayer2 extends NeptuneRpcStubNode {
    @NeptuneRpc()
    TestLayer2Rpc(a: number, b: string) {
        return new NeptuneRpcStubNode(null, this);
    }
}

class MirrorClientEntity extends NeptuneRpcEntityBase {
    rpcStub: MyNeptuneRpcStub;

    OnConnected() {
        console.log("Entity OnConnected");
        this.rpcStub.ServerRpc.Login("hello13").Perform();
        this.rpcStub.ServerRpc.GetGameServerPlayer().GameServerPlayerFooBarRpc(13).Perform();
    }

    TestRpc(a: number, b: string, c: number[]) {
        console.log("TestRpc", a, b, c);
        this.rpcStub.ServerRpc.TestRpc(1, "13").Perform();
    }

    GetLayer2() {
        return {TestLayer2Rpc: function (a: number, b: string) {
            console.log("testlayer2rpc", a, b);
        }};
    }
}

export class Neptune {
    rpcStub: MyNeptuneRpcStub;
    constructor() {

    }

    init() {
        let rpcStub = new MyNeptuneRpcStub({SendMessage: msg => console.error("stub messager not ready")});
        //let np_rpc_stub = new NeptuneRpcStringStub({SendMessage: (msg) => console.log("msgstr", msg)});        
        let mirrorEntity = new MirrorClientEntity();
        mirrorEntity.SetRpcStub(rpcStub);
        //mirrorEntity.SetRpcStub(np_rpc_stub);
        let msg = new NeptuneWSMessager(mirrorEntity);
        //msg.Connect("ws://echo.websocket.org");
        msg.Connect("ws://localhost:1317/13");

        //setTimeout(() => rpcStub.MirrorRpc.TestRpc(1, "13").Perform(), 5000);        
        //setTimeout(() => rpcStub.MirrorRpc.GetLayer2().TestLayer2Rpc(1, "13").Perform(), 5000);                
        //setTimeout(() => np_rpc_stub.RemoteCall("GetLayer2").RemoteCall("TestLayer2Rpc", 1, "13").Perform(), 5000);
    }
}


