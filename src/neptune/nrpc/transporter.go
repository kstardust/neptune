package nrpc

import (
	"io"
	"log"
	"neptune/tlv"

	"github.com/golang/protobuf/proto"
)

type RPCObserver interface {
	Update(r *RPC) error
}

type RPCTransporter struct {
	RWC       io.ReadWriteCloser
	observers []RPCObserver
	trpc      *RPC
}

func (t *RPCTransporter) notifyObservers() error {
	if t.trpc == nil {
		return nil
	}
	for _, observer := range t.observers {
		if err := observer.Update(t.trpc); err != nil {
			return err
		}
	}
	return nil
}

func (t *RPCTransporter) RegisterObserver(o RPCObserver) {
	t.observers = append(t.observers, o)
}

func (rpct *RPCTransporter) Serve() {
	if rpct.RWC == nil {
		log.Fatal("RWC is nil")
	}

	defer rpct.RWC.Close()
	for {
		t, err := tlv.ReadTLV(rpct.RWC)
		if err != nil {
			log.Printf("read tlv: %v\n", err)
			return
		}

		rpc := &RPC{}
		err = proto.Unmarshal(t.Value, rpc)
		if err != nil {
			log.Printf("unmarshal RPC: %v\n", err)
			return
		}
		rpct.trpc = rpc
		err = rpct.notifyObservers()
		if err != nil {
			log.Printf("notifyObservers error: %v\n", err)
			return
		}
	}
}
