package main

import (
	pb "go-grpc/src/proto"
	"io"
	"log"
	"net"

	"google.golang.org/grpc"
)

type server struct{}

func (s server) Max(srv pb.Math_MaxServer) error {
	log.Println("start new server")
	var max int32

	ctx := srv.Context()

	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
		}

		req, err := srv.Recv()
		if err == io.EOF {
			log.Println("exit")
			return nil
		}

		if err != nil {
			log.Println("receive error: %v", err)
			continue
		}

		if req.Num <= max {
			continue
		}

		max = req.Num
		resp := pb.Response{Result: max}
		if err := srv.Send(&resp); err != nil {
			log.Printf("send error %v", err)
		}

		log.Println("send new max=%d", max)
	}
}

func main() {
	lis, err := net.Listen("tcp", ":5005")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	s := grpc.NewServer()
	pb.RegisterMathServer(s, server{})

	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
