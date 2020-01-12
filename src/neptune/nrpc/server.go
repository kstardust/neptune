/*
   nrpc is basically the net/rpc package with customized codec extends
*/

package nrpc

import (
	"io"
	"log"
	"net/rpc"

	//	"github.com/golang/protobuf/proto"

	"net"
)

type NeptuneRpcServer rpc.Server

type NeptuneRpcCodec struct {
	rwc io.ReadWriteCloser
}

func (codec *NeptuneRpcCodec) ReadRequestHeader(*rpc.Request) error {
	return nil
}

func (codec *NeptuneRpcCodec) ReadRequestBody(interface{}) error {
	return nil
}

func (codec *NeptuneRpcCodec) WriteResponse(*rpc.Response, interface{}) error {
	return nil
}

// interface requirement: Close can be called multiple times and must be idempotent.
func (codec *NeptuneRpcCodec) Close() error {
	return nil
}

// ServerNeptune is the same as ServerConn except it uses a customized
// codec
func (server *NeptuneRpcServer) ServeNeptune(conn io.ReadWriteCloser) {
	// buf := bufio.NewWriter(conn)
	// srv := &NeptuneRpcCodec{
	// 	rwc: conn,
	// 	// dec:    gob.NewDecoder(conn),
	// 	// enc:    gob.NewEncoder(buf),
	// 	// encBuf: buf,
	// }
	//	server.ServeCodec(srv)
}

// AcceptNeptune is the same as Accept except it calls ServeNeptune
func (server *NeptuneRpcServer) AcceptNeptune(lis net.Listener) {
	for {
		conn, err := lis.Accept()
		if err != nil {
			log.Print("rpc.Serve: accept:", err.Error())
			return
		}
		go server.ServeNeptune(conn)
	}
}
