package main

import (
	"flag"
	"fmt"
	"io"
	"log"
	"neptune/wsadapter"
	"net/http"

	"github.com/gorilla/websocket"
)

var addr = flag.String("addr", "localhost:2019", "http service address")

var upgrader = websocket.Upgrader{
	// About buffer: https://godoc.org/github.com/gorilla/websocket#hdr-Buffers
	ReadBufferSize:  512,
	WriteBufferSize: 512,
	CheckOrigin:     func(r *http.Request) bool { return true },
}

type handlerType = func(http.ResponseWriter, *http.Request)

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

func main() {
	flag.Parse()
	log.SetFlags(0)
	http.HandleFunc("/", handler(echo))
	ws := new(wsadapter.WSAdapter)
	ws.DestAddr = "localhost:2020"
	http.HandleFunc("/adapter", handler(ws.Adapter))
	log.Fatal(http.ListenAndServe(*addr, nil))
}
