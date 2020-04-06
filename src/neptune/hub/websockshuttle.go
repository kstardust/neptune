package hub

import (
	"fmt"
	"log"

	"github.com/gorilla/websocket"
)

type WebSocketHub struct {
	*Hub
}

type WebSocketShuttle struct {
	*websocket.Conn
}

func (ws *WebSocketShuttle) DeliveryCargo(data []byte) error {
	error := ws.WriteMessage(websocket.TextMessage, data)
	return error
}

func (ws *WebSocketShuttle) Detach() {
	ws.Close()
}

func (wsh *WebSocketHub) Handler(c *websocket.Conn) error {
	_, message, err := c.ReadMessage()
	if err != nil {
		return fmt.Errorf("read meta error %v", err)
	}

	dockId := DockId(message)
	dock, ok := wsh.Docks[dockId]
	if !ok {
		return fmt.Errorf("Dock doesnt exist: %s", dockId)
	}

	shuttle := WebSocketShuttle{Conn: c}
	portId, error := dock.Port(&shuttle)
	if error != nil {
		log.Println("Port Error", error)
		return fmt.Errorf("Port Error: %v", error)
	}
	defer dock.Detach(portId)
	log.Println("connected: ", c.RemoteAddr())

	for {
		mt, message, err := c.ReadMessage()
		if err != nil {
			return fmt.Errorf("dock ReadMessage: %v", err)
		}
		log.Printf("dock recv: %d %v\n", mt, message)

		dock.Crane <- message
	}
}
