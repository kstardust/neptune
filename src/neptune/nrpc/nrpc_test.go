package nrpc

import (
	"bytes"
	"neptune/tlv"
	"testing"

	"github.com/golang/protobuf/proto"
)

type buffer struct {
	bytes.Buffer
}

func (b *buffer) Close() error {
	b.Buffer.Reset()
	return nil
}

func TestTransporter(t *testing.T) {
	req := &Request{
		Method: "test.protobuf",
		Args:   []byte("hello args"),
	}

	rpc := &RPC{
		Request: req,
	}

	data, err := proto.Marshal(rpc)
	if err != nil {
		t.Errorf("cannot marshal: %v\n", err)
	}

	tlvp := tlv.PackTLVMsg(0, data)

	rwc := &buffer{}
	_, err = rwc.Write(tlvp.Bytes())

	if err != nil {
		t.Errorf("write: %v\n", err)
	}

	tp := &Transporter{}
	tp.RWC = rwc
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
