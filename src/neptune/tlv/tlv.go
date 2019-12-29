package tlv

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"io"
	"log"
)

type TLV struct {
	Tag    uint16
	Length uint16
	Value  []byte
}

// Read a TLV struct
func ReadTLV(r io.Reader) (*TLV, error) {
	var record TLV
	err := binary.Read(r, binary.BigEndian, &record.Tag)
	if err == io.EOF {
		return nil, io.EOF
	} else if err != nil {
		return nil, fmt.Errorf("error reading TLV tag: %v", err)
	}

	err = binary.Read(r, binary.BigEndian, &record.Length)
	if err != nil {
		return nil, fmt.Errorf("error reading TLV length: %v", err)
	}
	record.Value = make([]byte, record.Length)
	_, err = io.ReadFull(r, record.Value)

	if err != nil {
		return nil, fmt.Errorf("error reading TLV value: %v", err)
	}

	return &record, nil
}

// Write a TLV struct
func WriteTLV(w io.Writer, tlv *TLV) error {

	// Write to a buffer first, then copy to destination,
	// I am imitating a batch write operaton here(writev)
	// to reduce system calls(when destination is a socket
	// or a file, and so forth)
	b := new(bytes.Buffer)

	err := binary.Write(b, binary.BigEndian, tlv.Tag)
	if err != nil {
		return fmt.Errorf("write Length: %v", err)
	}

	err = binary.Write(b, binary.BigEndian, tlv.Length)
	if err != nil {
		return fmt.Errorf("write Length: %v", err)
	}

	err = binary.Write(b, binary.BigEndian, tlv.Value)
	if err != nil {
		return fmt.Errorf("write Payload: %v", err)
	}

	_, err = io.Copy(w, b)
	return err
}

func DisplayTLV(t *TLV) {
	log.Printf("tag: %v, length: %v, content: %v", t.Tag, t.Length, t.Value)
}
