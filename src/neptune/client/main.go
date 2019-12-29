package main

import (
	"bytes"
	"log"
	"neptune/tlv"
	"time"

	"net"
)

func main() {
	a := []string{"hello world", "foobar", "barfoo"}

	conn, err := net.Dial("tcp", "localhost:2019")
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()

	for _, msg := range a {
		t := tlv.TLV{}
		t.Tag = 1
		t.Value = []byte(msg)
		t.Length = uint16(len(t.Value))

		var bf bytes.Buffer
		tlv.WriteTLV(&bf, &t)

		bs := bf.Bytes()
		conn.Write(bs[:5])
		log.Printf("first half")
		time.Sleep(time.Second * 5)
		conn.Write(bs[5:])
		log.Printf("second half")
		time.Sleep(time.Second * 1)
	}
}
