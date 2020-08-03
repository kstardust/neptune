package main

import (
	"log"
	pb "neptune/src/proto"
	"neptune/src/room"
	"neptune/src/server"
	"net"

	"google.golang.org/grpc"
)

func main() {
	lis, err := net.Listen("tcp", ":5005")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	s := grpc.NewServer()
	st := server.NewServer(func(r *room.Room) error {
		log.Printf("start run game logic in room: %s", r.Id)
		for {
			req := <-r.GetInput()
			log.Printf("input: %v", req)
			for _, p := range r.Players {
				p.SendMessage(req.GetPayload())
			}
		}
	})

	pb.RegisterNeptuneServer(s, st)

	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
