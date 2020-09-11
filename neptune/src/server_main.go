// package main

// import (
// 	"log"
// 	"neptune/src/logic"
// 	pb "neptune/src/proto"
// 	"neptune/src/server"
// 	"net"

// 	"google.golang.org/grpc"
// )

// func main() {
// 	lis, err := net.Listen("tcp", ":5005")
// 	if err != nil {
// 		log.Fatalf("failed to listen: %v", err)
// 	}

// 	s := grpc.NewServer()
// 	st := server.NewServer(logic.Logic)

// 	pb.RegisterNeptuneServer(s, st)

// 	if err := s.Serve(lis); err != nil {
// 		log.Fatalf("failed to serve: %v", err)
// 	}
// }
package main

import (
	"neptune/src/discovery"
	"neptune/src/skeleton"
)

func main() {
	server := &skeleton.NeptuneServerSkeleton{}
	var service skeleton.MyService
	dis := new(discovery.DiscoveryServiceClient)
	server.AddService("discovery", dis)
	server.AddService("foobar", service)
	server.Run()
}
