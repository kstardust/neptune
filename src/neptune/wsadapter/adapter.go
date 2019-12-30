package wsadapter

import (
	"fmt"
	"log"

	"github.com/gorilla/websocket"
)

func Adapter(c *websocket.Conn) error {
	for {
		mt, message, err := c.ReadMessage()
		if err != nil {
			return fmt.Errorf("echo ReadMessage: %v", err)
		}
		log.Printf("recv: %v\n", message)

		err = c.WriteMessage(mt, message)
		if err != nil {
			return fmt.Errorf("echo WriteMessage: %v", err)
		}
	}
}
