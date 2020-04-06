package main

import (
	"flag"
	"fmt"
	"io"
	"log"
	"neptune/hub"
	"net/http"
	"strconv"

	"github.com/gorilla/websocket"
)

var addr = flag.String("addr", "localhost:2019", "http service address")
var defaultFps = flag.Int64("fps", 20, "fps")

var upgrader = websocket.Upgrader{
	// About buffer: https://godoc.org/github.com/gorilla/websocket#hdr-Buffers
	ReadBufferSize:  512,
	WriteBufferSize: 512,
	CheckOrigin:     func(r *http.Request) bool { return true },
}

type handlerType = func(http.ResponseWriter, *http.Request)

func websocketWrapper(f func(*websocket.Conn) error) handlerType {
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

type HubHttp struct {
	hub *hub.Hub
}

func (hbhp *HubHttp) new(w http.ResponseWriter, r *http.Request) {
	values, ok := r.URL.Query()["ships"]
	var ships int64
	if ok {
		value := values[0]
		num, err := strconv.ParseInt(value, 10, 64)
		if err == nil {
			ships = num
		}
	}

	if ships <= 0 {
		w.Write([]byte(fmt.Sprintf("{\"msg\": \"invalid ships.\"}\n")))
		return
	}

	values, ok = r.URL.Query()["fps"]
	fps := *defaultFps

	if ok {
		value := values[0]
		num, err := strconv.ParseInt(value, 10, 64)
		if err != nil || num < 60 || num > 0 {
			fps = num
		}
	}

	dock, id := hbhp.hub.NewDock(ships, fps)
	if dock == nil {
		w.Write([]byte(fmt.Sprintf("{\"msg\": \"cannot create new dock.\"}\n")))
		return
	}
	go dock.SetTheBallRolling()

	w.Write([]byte(fmt.Sprintf("{\"dock\": \"%s\", \"fps\": %d}\n", id, fps)))
}

func (hbhp *HubHttp) end(w http.ResponseWriter, r *http.Request) {
	values, ok := r.URL.Query()["dock"]
	if ok {
		did := values[0]
		hbhp.hub.FreeDock(hub.DockId(did))
	}
}

func main() {
	flag.Parse()
	hb := hub.NewHub()
	wshub := hub.WebSocketHub{Hub: hb}

	hbhttp := HubHttp{hub: hb}
	http.HandleFunc("/", websocketWrapper(echo))
	http.HandleFunc("/new", hbhttp.new)
	http.HandleFunc("/stop", hbhttp.end)
	http.HandleFunc("/neptune", websocketWrapper(wshub.Handler))

	log.Fatal(http.ListenAndServe(*addr, nil))
}
