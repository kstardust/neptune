package wsadapter

import (
	"fmt"
	"log"
	"neptune/tlv"

	"github.com/gorilla/websocket"
)

type WSAdapter struct {
	DestAddr string
}

func (w *WSAdapter) Adapter(c *websocket.Conn) error {
	// destc, err := net.Dial("tcp", w.DestAddr)
	// if err != nil {
	// 	return fmt.Errorf("WSAdapter Dial: %v", err)
	// }

	for {
		mt, message, err := c.ReadMessage()
		if err != nil {
			return fmt.Errorf("adapter ReadMessage: %v", err)
		}
		log.Printf("recv: %v\n", message)

		t := tlv.PackTLVMsg(0, message)
		err = c.WriteMessage(mt, t.Bytes())
		if err != nil {
			return fmt.Errorf("adapter WriteMessage: %v", err)
		}
	}
}
