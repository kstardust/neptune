package nrpc

import (
	"bytes"
	"log"
	"neptune/tlv"
	"net/rpc"
	"testing"

	"github.com/golang/protobuf/proto"
)

type buffer struct {
	bytes.Buffer
}

type TestService int

func (t *TestService) Foobar(args *Request, reply *Response) error {
	log.Println("remote process call", args)
	reply.Response = []byte("hello response")
	return nil
}

func (b *buffer) Close() error {
	b.Buffer.Reset()
	return nil
}

func TestTransporter(t *testing.T) {
	pseudoArgs := &Request{
		Method: "pseudoArgs",
		Args:   []byte("pseudoArgs"),
	}

	pseudoArgsBytes, err := proto.Marshal(pseudoArgs)
	if err != nil {
		t.Errorf("cannot marshal args: %v\n", err)
	}

	req := &Request{
		Method: "TestService.Foobar",
		Args:   pseudoArgsBytes,
	}

	rpc_ := &RPC{
		Request: req,
		Sid:     123,
	}

	data, err := proto.Marshal(rpc_)
	if err != nil {
		t.Errorf("cannot marshal: %v\n", err)
	}

	tlvp := tlv.PackTLVMsg(0, data)

	rwc := &buffer{}
	_, err = rwc.Write(tlvp.Bytes())

	if err != nil {
		t.Errorf("write: %v\n", err)
	}

	tp := &RPCTransporter{}
	tp.Mesger = &tlv.TLVCodec{
		RWC: rwc,
	}

	tss := new(TestService)

	err = rpc.Register(tss)
	if err != nil {
		t.Errorf("register %v", err)
	}

	codec := new(NeptuneRpcCodec)
	tp.RegisterObserver(codec)

	tp.Serve()
}

func TestProtobuf(t *testing.T) {
	req := &Request{
		Method: "test.protobuf",
		Args:   []byte("args"),
	}

	rpc := &RPC{
		Request: req,
	}

	data, err := proto.Marshal(rpc)

	if err != nil {
		t.Errorf("cannot marshal: %v\n", err)
	}

	t.Log(data)

	var newrpc RPC
	err = proto.Unmarshal(data, &newrpc)

	if err != nil {
		t.Errorf("cannot marshal: %v\n", err)
	}

	t.Log(newrpc.GetRequest().GetMethod())
}
