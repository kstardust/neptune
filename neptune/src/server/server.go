package main

import (
	"context"
	"io"
	"log"
	pb "neptune/src/proto"
	"neptune/src/room"
	"net"

	"google.golang.org/grpc"
)

type server struct {
	Rooms map[room.RoomId]*room.Room
}

func (s server) CreateRoom(ctx context.Context, srv *pb.CreateRoomRequest) (*pb.CreateRoomResponse, error) {
	log.Println("create room %v", srv)
	r, _ := room.New(nil)
	for _, ok := s.Rooms[r.Id]; ok; {
		r, _ = room.New(nil)
	}

	s.Rooms[r.Id] = r

	return &pb.CreateRoomResponse{RoomId: string(r.Id), Secret: r.Secret}, nil
}

func (s server) JoinRoom(ctx context.Context, srv *pb.JoinRoomRequest) (*pb.JoinRoomResponse, error) {
	log.Println("join room %v", srv)
	return &pb.JoinRoomResponse{}, nil
}

func (s server) Stream(srv pb.Neptune_StreamServer) error {
	log.Println("stream begin")

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

		max = req.Num
		resp := pb.Response{Result: max}
		if err := srv.Send(&resp); err != nil {
			log.Printf("send error %v", err)
		}

		log.Println("send new max=%d", max)
	}
}

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
	st := server{Rooms: make(map[room.RoomId]*room.Room)}
	pb.RegisterMathServer(s, st)
	pb.RegisterNeptuneServer(s, st)

	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
