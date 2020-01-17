/*
   nrpc is basically the net/rpc package with customized codec extends
*/

package nrpc

import (
	"fmt"
	"github.com/golang/protobuf/proto"
	"io"
	"log"
	"neptune/tlv"
	"net/rpc"

	"net"
)

type NeptuneRpcServer rpc.Server

type NeptuneRpcCodec struct {
	request  *RPC
	response *RPC
}

func (codec *NeptuneRpcCodec) ReadRequestHeader(r *rpc.Request) error {
	r.ServiceMethod = codec.request.GetRequest().GetMethod()
	r.Seq = uint64(codec.request.GetSid())
	return nil
}

func (codec *NeptuneRpcCodec) ReadRequestBody(body interface{}) error {
	err := proto.Unmarshal(codec.request.GetRequest().GetArgs(), body.(proto.Message))
	if err != nil {
		return fmt.Errorf("ReadRequestBody: %v", err)
	}
	return nil
}

func (codec *NeptuneRpcCodec) WriteResponse(resp *rpc.Response, reply interface{}) error {
	replyData, err := proto.Marshal(reply.(proto.Message))
	if err != nil {
		return err
	}

	codec.response = &RPC{}
	codec.response.Sid = uint32(resp.Seq)
	codec.response.Response = &Response{}
	codec.response.Response.Response = replyData

	return nil
}

// interface requirement: Close can be called multiple times and must be idempotent.
func (codec *NeptuneRpcCodec) Close() error {
	// stub TBD
	return nil
}

func (codec *NeptuneRpcCodec) Update(r *RPC) (*RPC, error) {
	if r.GetRequest() == nil {
		return nil, nil
	}

	codec.request = r
	err := rpc.ServeRequest(codec)
	if err != nil {
		return nil, err
	}
	return nil, nil
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
		rpct := RPCTransporter{}
		rpct.Mesger = &tlv.TLVCodec{
			RWC: conn,
		}
		go rpct.Serve()
	}
}
