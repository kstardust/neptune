import { NeptuneRpc, NeptuneRpcStringStub, NeptuneRpcExecutor, NeptuneRpcStubNode, NeptuneRpcStub } from "./neptune/skeleton/remote_call";
import { NeptuneWSMessager } from "./neptune/skeleton/ws_messager";
import { NeptuneRpcEntityBase } from "./neptune/skeleton/net_entity"

const {ccclass, property} = cc._decorator;

class BarRpcStub extends NeptuneRpcStubNode {
    @NeptuneRpc()
    NestedRpc(z: number[]): NeptuneRpcStubNode {
        return new NeptuneRpcStubNode(null, this);
    }
}

class FooRpcStub extends NeptuneRpcStubNode {
    @NeptuneRpc()
    GetBar(): BarRpcStub {
        return new BarRpcStub(null, this);
    }

    @NeptuneRpc()
    TestRpc(a: number, b: string): NeptuneRpcStubNode {
        return new NeptuneRpcStubNode(null, this);
    }
}

class MyNeptuneRpcStub extends NeptuneRpcStub {
    // add root stub declarations at here
    ServerRpc: FooRpcStub;
    MirrorRpc: MirrorClientRpc;

    InitRpcStubs() {
        // create root stubs at here
        this.ServerRpc = new FooRpcStub(this);
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


@ccclass
export default class Helloworld extends cc.Component {

    @property(cc.Label)
    label: cc.Label = null;

    @property
    text: string = 'hello13';

    start () {
        // init logic
        this.label.string = this.text;

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

    update(dt: number) {
        
    } 
}
