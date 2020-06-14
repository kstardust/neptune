package hello

import (
	"log"

	"golang.org/x/net/context"
)

type Server struct {
}

func (s *Server) SayHello(ctx context.Context, in *HelloRequest) (*HelloReply, error) {
	log.Printf("gRPC SayHello request: %v\n", in.Name)
	return &HelloReply{Message: "hello world"}, nil
}
