package core

import (
	"context"
	hellopb "neptuneNG/hello"

	"google.golang.org/grpc"

	"fmt"
	"log"
	"net"
)

func ServerMain() {
	fmt.Println("test grpc")

	lis, err := net.Listen("tcp", "0.0.0.0:9900")
	if err != nil {
		log.Fatalf("cannot listen: %v", err)
	}

	s := hellopb.Server{}
	grpcServer := grpc.NewServer()
	hellopb.RegisterGreeterServer(grpcServer, &s)

	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("cannot serve: %v", err)
	}
}

func ClientMain() {
	fmt.Println("test grpc client")

	var conn *grpc.ClientConn
	conn, err := grpc.Dial(":9900", grpc.WithInsecure())
	if err != nil {
		log.Fatalf("cannot dial: %v", err)
	}

	defer conn.Close()

	c := hellopb.NewGreeterClient(conn)

	response, err := c.SayHello(context.Background(), &hellopb.HelloRequest{Name: "dumb client"})
	if err != nil {
		log.Fatalf("cannot call SayHello: %v", err)
	}

	log.Printf("response: %v", response)

}
