import { NeptuneRpc, NeptuneRpcStringStub, NeptuneRpcExecutor, NeptuneRpcStubNode, NeptuneRpcStub } from "./neptune/skeleton/remote_call";

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
    FooRpc: FooRpcStub;

    InitRpcStubs() {
        // create root stubs at here
        this.FooRpc = new FooRpcStub(this);
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
        //let np_rpc_stub = new NeptuneRpcStringStub(null);
        let np_rpc = new NeptuneRpcExecutor(this);
        //let message = np_rpc_stub.RemoteCall("TestRpc", 13, "13", [1, 3]).Perform();
        //np_rpc.Execute(message);
        let np_stub = new MyNeptuneRpcStub({SendMessage: (msg) => console.log("msg", msg)});
        np_stub.FooRpc.TestRpc(13, "hello").Perform();
        np_stub.FooRpc.GetBar().NestedRpc([1, 2]).Perform();
    }
        
    TestRpc(a: number, b: string, c: number[]) {
        console.log("TestRpc", a, b, c);
    }

    update(dt: number) {
        
    } 
}
