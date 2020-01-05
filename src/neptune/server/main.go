package main

import (
	"io"
	"log"
	"neptune/tlv"

	"net"
)

func handle(c net.Conn) {
	defer c.Close()

	for {
		msg, err := tlv.ReadTLV(c)
		if err == io.EOF {
			log.Printf("connection closed")
			return
		}

		if err != nil {
			log.Printf("error ReadTLV: %v", err)
			return
		}
		tlv.DisplayTLV(msg)
		err = msg.Write(c)
		if err != nil {
			log.Printf("error writeTLV: %v", err)
			return
		}
	}
}

func main() {
	listener, err := net.Listen("tcp", "localhost:2020")
	if err != nil {
		log.Fatal(err)
	}
	defer listener.Close()

	for {
		conn, err := listener.Accept()
		if err != nil {
			log.Printf("error accept: %v", err)
			continue
		}

		go handle(conn)
	}

	// t := tlv.TLV{}
	// t.Tag = 1
	// t.Value = []byte("Hello World")
	// t.Length = uint16(len(t.Value))

	// var buf bytes.Buffer
	// err = tlv.WriteTLV(&buf, &t)
	// if err != nil {
	// 	log.Fatal(err)
	// }

	// fmt.Println(buf.Bytes())
	// r, err := tlv.ReadTLV(&buf)
	// if err != nil {
	// 	log.Fatal(err)
	// }
	// tlv.DisplayTLV(r)
}
