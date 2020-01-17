package tlv

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"io"
	"log"
)

type TLVCodec struct {
	Tag uint16
	RWC io.ReadWriteCloser
}

type TLV struct {
	Tag    uint16
	Length uint16
	Value  []byte
}

func (codec *TLVCodec) Close() {
	if codec.RWC != nil {
		codec.RWC.Close()
	}

	codec.RWC = nil
}

func (codec *TLVCodec) ReadMessage() ([]byte, error) {
	if codec.RWC == nil {
		log.Fatal("TLVCode rw is nil")
	}

	t, err := ReadTLV(codec.RWC)
	if err != nil {
		return nil, fmt.Errorf("TLVCodec ReadMessage: %v\n", err)
	}
	return t.Value, nil
}

func (codec *TLVCodec) SendMessage(msg []byte) error {
	if codec.RWC == nil {
		log.Fatal("TLVCode rw is nil")
	}

	if _, err := codec.RWC.Write(PackTLVMsg(codec.Tag, msg).Bytes()); err != nil {
		return fmt.Errorf("TLVCodec SendMessage: %v", err)
	}
	return nil
}

// pack a message
func PackTLVMsg(tag uint16, msg []byte) *TLV {
	t := new(TLV)
	t.Tag = tag
	t.Value = msg
	t.Length = uint16(len(msg))
	return t
}

// Read a TLV struct
func ReadTLV(r io.Reader) (*TLV, error) {
	var record TLV
	err := binary.Read(r, binary.BigEndian, &record.Tag)
	if err == io.ErrUnexpectedEOF {
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
	_, err := w.Write(tlv.Bytes())
	return err
}

// Write a TLV struct
func (t *TLV) Write(w io.Writer) error {
	return WriteTLV(w, t)
}

// Read a TLV struct
func (t *TLV) Read(r io.Reader) error {
	tlv, error := ReadTLV(r)
	if error != nil {
		return error
	}
	*t = *tlv
	return nil
}

// Return bytes of a TLV struct
func (t *TLV) Bytes() []byte {
	b := new(bytes.Buffer)

	err := binary.Write(b, binary.BigEndian, t.Tag)
	if err != nil {
		log.Fatalf("TLV Bytes, write Length: %v", err)
	}

	err = binary.Write(b, binary.BigEndian, t.Length)
	if err != nil {
		log.Fatalf("TLV Bytes, write Length: %v", err)
	}

	err = binary.Write(b, binary.BigEndian, t.Value)
	if err != nil {
		log.Fatalf("TLV Bytes, write Payload: %v", err)
	}

	return b.Bytes()
}

func DisplayTLV(t *TLV) {
	log.Printf("tag: %v, length: %v, content: %v", t.Tag, t.Length, t.Value)
}
