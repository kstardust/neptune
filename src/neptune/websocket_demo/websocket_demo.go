package websocket_demo

import (
	"flag"
	"log"
	"net/http"
	"os"

	"github.com/gorilla/websocket"
)

type Messager interface {
	ReadMessage() ([]byte, int, error)
	SendMessage(msg []byte) error
	Close() error
}

var upgrader = websocket.Upgrader{CheckOrigin: func(r *http.Request) bool { return true }}

var addr = flag.String("addr", "localhost:2019", "http service address")

func echo(w http.ResponseWriter, r *http.Request) {
	c, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("upgrade: ", err)
		return
	}
	defer c.Close()

	for {
		mt, message, err := c.ReadMessage()
		if err != nil {
			log.Println("ReadMessage: ", err)
			break
		}
		log.Printf("recv: %v\n", message)

		err = c.WriteMessage(mt, message)
		if err != nil {
			log.Println("write: ", err)
			return
		}
	}
}

func main() {
	flag.Parse()
	log.SetFlags(0)
	http.HandleFunc("/", echo)
	log.Println(os.Args[0], os.Args[1:], os.Environ())
	log.Fatal(http.ListenAndServe(*addr, nil))
}
