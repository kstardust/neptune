package nrpc

import (
	"fmt"
	"log"

	"github.com/golang/protobuf/proto"
)

type RPCObserver interface {
	Update(r *RPC) (*RPC, error)
}

type Messenger interface {
	ReadMessage() ([]byte, error)
	SendMessage(msg []byte) error
	Close()
}

type RPCTransporter struct {
	Mesger    Messenger
	observers []RPCObserver
	trpc      *RPC
}

func (t *RPCTransporter) notifyObservers() error {
	if t.trpc == nil {
		return nil
	}
	for _, observer := range t.observers {
		reply, err := observer.Update(t.trpc)
		if err != nil {
			// may add observer type info later
			return fmt.Errorf("notifyObservers: Update Observer: %v", err)
		}

		if reply == nil {
			return nil
		}

		replyData, err := proto.Marshal(reply)
		if err != nil {
			return fmt.Errorf("notifyObservers: Cannot Marshal: %v", err)
		}

		if err = t.Mesger.SendMessage(replyData); err != nil {
			return fmt.Errorf("notifyObservers: Write Reply: %v", err)
		}
	}
	t.trpc = nil
	return nil
}

func (t *RPCTransporter) RegisterObserver(o RPCObserver) {
	t.observers = append(t.observers, o)
}

func (rpct *RPCTransporter) Serve() {
	if rpct.Mesger == nil {
		log.Fatal("messenger is nil")
	}

	defer rpct.Mesger.Close()
	for {
		bytes, err := rpct.Mesger.ReadMessage()
		if err != nil {
			log.Printf("read message: %v\n", err)
			return
		}

		rpc := &RPC{}
		err = proto.Unmarshal(bytes, rpc)
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
