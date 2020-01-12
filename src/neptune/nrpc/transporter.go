package nrpc

import (
	"io"
	"log"
	"neptune/tlv"

	"github.com/golang/protobuf/proto"
)

type Transporter struct {
	RWC io.ReadWriteCloser
}

func (t *Transporter) Serve() {
	if t.RWC == nil {
		log.Fatal("RWC is nil")
	}

	defer t.RWC.Close()
	for {
		t, err := tlv.ReadTLV(t.RWC)
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
		log.Println(rpc)
	}
}
