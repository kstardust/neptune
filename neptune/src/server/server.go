package server

import (
	"context"
	"fmt"
	"io"
	"log"
	pb "neptune/src/proto"
	"neptune/src/room"
)

type NeptuneServer struct {
	Rooms   map[room.RoomId]*room.Room
	Players map[room.PlayerId]room.Player
	logic   room.GameLogic
}

func NewServer(logic room.GameLogic) *NeptuneServer {
	return &NeptuneServer{
		Rooms:   make(map[room.RoomId]*room.Room),
		Players: make(map[room.PlayerId]room.Player),
		logic:   logic,
	}
}

func (s *NeptuneServer) NewRoom() *room.Room {
	if len(s.Rooms) == 0 {
		r, _ := room.New()
		s.Rooms[r.Id] = r
	}

	for _, v := range s.Rooms {
		return v
	}
	// r, _ := room.New()
	// for _, ok := s.Rooms[r.Id]; ok; {
	// 	r, _ = room.New()
	// }

	// s.Rooms[r.Id] = r
	// return r
	return nil
}

func (s *NeptuneServer) NewPlayer(playerId room.PlayerId) room.Player {
	player := room.NewPlayer(playerId)
	s.Players[playerId] = player
	return player
}

func (s *NeptuneServer) RegisterPlayer(player room.Player, roomId room.RoomId) {
	s.Players[player.Id()] = player
}

func (s *NeptuneServer) CreateRoom(ctx context.Context, srv *pb.CreateRoomRequest) (*pb.CreateRoomResponse, error) {
	log.Printf("create room %v", srv)

	r := s.NewRoom()
	go r.Run(s.logic)
	return &pb.CreateRoomResponse{RoomId: string(r.Id), Secret: r.Secret}, nil
}

func (s *NeptuneServer) JoinRoom(ctx context.Context, srv *pb.JoinRoomRequest) (*pb.JoinRoomResponse, error) {
	log.Printf("player [%s] is trying to join room [%s]", srv.PlayerId, srv.RoomId)

	player, ok := s.Players[room.PlayerId(srv.PlayerId)]
	if ok {
		player.SetStatus(room.PlayerStatusConnected)
		log.Printf("player [%s] is already in room [%s]", player.Id, player.Room())
		return &pb.JoinRoomResponse{Code: pb.ErrorCode_OK, RoomId: string(player.Room())}, nil
	}

	r, ok := s.Rooms[room.RoomId(srv.RoomId)]
	if !ok {
		return &pb.JoinRoomResponse{Code: pb.ErrorCode_FAILED}, nil
	}

	player = s.NewPlayer(room.PlayerId(srv.PlayerId))
	r.PlayerJoin(player)
	player.SetStatus(room.PlayerStatusConnected)

	return &pb.JoinRoomResponse{RoomId: string(r.Id)}, nil
}

func (s *NeptuneServer) Stream(srv pb.Neptune_StreamServer) error {
	log.Println("stream begin")

	ctx := srv.Context()

	var room_ *room.Room
	var player room.Player

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
			var ok bool
			player, ok = s.Players[playerId]

			if !ok {
				msg := fmt.Sprintf("no such player: %v", playerId)
				log.Println(msg)
				return fmt.Errorf(msg)
			}

			room_, ok = s.Rooms[player.Room()]

			if room_ == nil {
				msg := fmt.Sprintf("no such room %v for player: %v", player.Room(), playerId)
				log.Println(msg)
				return fmt.Errorf(msg)
			}

			player.SetStatus(room.PlayerStatusStreaming)
			player.SetRpcBackend(srv)

			defer func() {
				room_.PlayerStopStream(player)
			}()
		}

		room_.Input() <- req
	}
	return nil
}
