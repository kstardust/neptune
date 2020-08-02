package main

import (
	"context"
	"fmt"
	"io"
	"log"
	pb "neptune/src/proto"
	"neptune/src/room"
	"net"

	"google.golang.org/grpc"
)

type server struct {
	Rooms   map[room.RoomId]*room.Room
	Players map[room.PlayerId]room.RoomId
}

func (s *server) NewRoom() *room.Room {
	r, _ := room.New(nil)
	for _, ok := s.Rooms[r.Id]; ok; {
		r, _ = room.New(nil)
	}

	s.Rooms[r.Id] = r
	return r
}

func (s *server) RegisterPlayer(playerId room.PlayerId, roomId room.RoomId) error {
	_, exist := s.Players[playerId]
	if exist {
		return fmt.Errorf("player %s already in room %s", playerId, roomId)
	}

	s.Players[playerId] = roomId
	return nil
}

func (s *server) GetRoomOfPlayer(playerId room.PlayerId) *room.Room {
	roomId, ok := s.Players[playerId]
	if !ok {
		return nil
	}

	return s.Rooms[roomId]
}

func (s *server) CreateRoom(ctx context.Context, srv *pb.CreateRoomRequest) (*pb.CreateRoomResponse, error) {
	log.Printf("create room %v", srv)

	r := s.NewRoom()
	go r.Run(func(room *room.Room) error {
		log.Printf("start run game logic in room: %s", r.Id)
		for {
			resp := <-room.GetInput()
			log.Printf("input: %v", resp)
		}
	})
	return &pb.CreateRoomResponse{RoomId: string(r.Id), Secret: r.Secret}, nil
}

func (s *server) JoinRoom(ctx context.Context, srv *pb.JoinRoomRequest) (*pb.JoinRoomResponse, error) {
	log.Printf("player [%s] is trying to join room [%s]", srv.PlayerId,  srv.RoomId)
	r, ok := s.Rooms[room.RoomId(srv.RoomId)]
	if !ok {
		return &pb.JoinRoomResponse{Code: pb.ErrorCode_FAILED}, nil
	}

	roomId, ok := s.Players[room.PlayerId(srv.PlayerId)]
	if ok {
		return &pb.JoinRoomResponse{Code: pb.ErrorCode_FAILED, RoomId: string(roomId)}, nil
	}

	player := room.NewBasicPlayer(room.PlayerId(srv.PlayerId))
	s.RegisterPlayer(player.Id(), r.Id)
	r.PlayerJoin(player)
	return &pb.JoinRoomResponse{RoomId: string(r.Id)}, nil
}

func (s *server) Stream(srv pb.Neptune_StreamServer) error {
	log.Println("stream begin")

	ctx := srv.Context()

	var room_ *room.Room
	
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
		}

		req, err := srv.Recv()
		if err == io.EOF {
			log.Println("stream exit")
			return nil
		}

		if err != nil {
			log.Println("receive error: %v", err)
			continue
		}

		if room_ == nil {
			playerId := room.PlayerId(req.PlayerId)
			room_ = s.GetRoomOfPlayer(playerId)

			if room_ == nil {
				msg := fmt.Sprintf("cannot locate player: %v", playerId)
				log.Println(msg)
				return fmt.Errorf(msg)
			}

			defer func() {
				room_.PlayerStopStream(playerId)
			}()
		}

		room_.Input() <- req
	}
	return nil
}

func (s *server) Max(srv pb.Math_MaxServer) error {
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
	st := &server{
		Rooms:   make(map[room.RoomId]*room.Room),
		Players: make(map[room.PlayerId]room.RoomId),
	}
	//	pb.RegisterMathServer(s, st)
	pb.RegisterNeptuneServer(s, st)

	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
