package main

import (
	"flag"
	"fmt"
	"io"
	"log"
	"neptune/hub"
	"net/http"

	"github.com/gorilla/websocket"
)

var addr = flag.String("addr", "localhost:2019", "http service address")
var fps = flag.Int64("fps", 20, "fps")

var upgrader = websocket.Upgrader{
	// About buffer: https://godoc.org/github.com/gorilla/websocket#hdr-Buffers
	ReadBufferSize:  512,
	WriteBufferSize: 512,
	CheckOrigin:     func(r *http.Request) bool { return true },
}

type handlerType = func(http.ResponseWriter, *http.Request)
type wsHandlerType = func(c *websocket.Conn) error

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

func handler(f func(*websocket.Conn) error) handlerType {
	return func(w http.ResponseWriter, r *http.Request) {
		log.Println(r.URL)
		c, err := upgrader.Upgrade(w, r, nil)
		if err != nil {
			log.Println("upgrade: ", err)
			return
		}
		defer c.Close()

		err = f(c)
		if err != io.EOF && err != nil {
			log.Println("handler: ", err)
		}
	}
}

func echo(c *websocket.Conn) error {
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

func dockHandler(dock *hub.Dock) wsHandlerType {
	return func(c *websocket.Conn) error {
		shuttle := WebSocketShuttle{Conn: c}
		portId := dock.Port(&shuttle)
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
}

func main() {
	flag.Parse()
	dock := hub.Dock{}
	http.HandleFunc("/", handler(echo))
	dhandler := dockHandler(&dock)
	go dock.SetTheBallRolling(*fps)
	http.HandleFunc("/neptune", handler(dhandler))
	log.Fatal(http.ListenAndServe(*addr, nil))
}
