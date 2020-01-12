package wsadapter

import (
	"fmt"
	"io"
	"log"
	"neptune/tlv"

	"net"

	"github.com/gorilla/websocket"
)

type WSAdapter struct {
	DestAddr string
}

func (w *WSAdapter) Adapter(c *websocket.Conn) error {
	destc, err := net.Dial("tcp", w.DestAddr)
	destDone := make(chan error)
	cliDone := make(chan error)

	if err != nil {
		return fmt.Errorf("WSAdapter Dial: %v", err)
	}

	go func() {
		// dest -> client
		for {
			t, err := tlv.ReadTLV(destc)
			if err == io.EOF {
				destDone <- nil 
			}
			if err != nil {
				destDone <- fmt.Errorf("adapter Read dest: %v", err)
				return
			}

			if err = c.WriteMessage(websocket.BinaryMessage, t.Value); err != nil {
				destDone <- fmt.Errorf("adapter WriteMessage cli: %v", err)
				return
			}
		}
	}()

	go func() {
		// client -> dest
		for {
			mt, message, err := c.ReadMessage()
			if mt != websocket.BinaryMessage {
				cliDone <- fmt.Errorf("not binary message, type: %v", mt)
				return
			}
			if len(message) == 0 {
				cliDone <- fmt.Errorf("empty message")
				return
			}
			if err != nil {
				cliDone <- fmt.Errorf("adapter ReadMessage cli: %v", err)
				return
			}
			log.Printf("cli recv: %v %v\n", mt, message)

			t := tlv.PackTLVMsg(0, message)
			if err = t.Write(destc); err != nil {
				cliDone <- fmt.Errorf("adapter Write dest: %v", err)
				return
			}
		}
	}()

	for i := 0; i < 2; i++ {
		select {
		case err = <-destDone:
			log.Printf("dest Done: %v\n", err)
		case err = <-cliDone:
			log.Printf("cli Done: %v\n", err)
		}

		if i == 0 {
			destc.Close()
			c.Close()
		}
	}
	log.Printf("finished\n")
	return nil
}
