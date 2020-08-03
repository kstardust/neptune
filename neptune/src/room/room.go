package room

import (
	"log"
	"math/rand"
	pb "neptune/src/proto"
)

type RoomId string
type GameLogic = func(room *Room) error

type Room struct {
	Id      RoomId
	Players []Player
	Secret  string
	input   chan *pb.StreamRequest
	running bool
}

var Letters = []rune("abcdefghijklmnopqrstuvwxyz0123456789")

func generateRandomSeq(length uint) string {
	res := make([]rune, length)
	for i := range res {
		res[i] = Letters[rand.Intn(len(Letters))]
	}
	return string(res)
}

func newRoom(players uint, roomIdlength uint, cmdBuffer int) (*Room, error) {
	room := new(Room)
	room.Id = RoomId(generateRandomSeq(4))
	room.Players = make([]Player, 0, players)
	room.Secret = generateRandomSeq(12)
	room.input = make(chan *pb.StreamRequest, cmdBuffer)
	return room, nil
}

func (r *Room) Input() chan<- *pb.StreamRequest {
	return r.input
}

func (r *Room) GetInput() <-chan *pb.StreamRequest {
	return r.input
}

func (r *Room) Run(logic GameLogic) {
	if r.running {
		log.Println("this room is already running its logic.")
		return
	}
	log.Println("start to run game logic")
	defer func() {
		// TODO: recover from panic
		log.Println("game logic end")
	}()

	r.running = true
	logic(r)
}

func (r *Room) Cap() int {
	return cap(r.Players)
}

func (r *Room) PlayerCnt() int {
	return len(r.Players)
}

func (r *Room) PlayerJoin(p Player) error {
	log.Printf("player [%s] joined room", p.Id())
	p.SetRoom(r.Id)
	r.Players = append(r.Players, p)
	return nil
}

func (r *Room) PlayerStopStream(p Player) {
	log.Printf("player [%s] stop stream", p)
	p.SetStatus(PlayerStatusDisconnect)
}

func New() (*Room, error) {
	return newRoom(2, 4, 100)
}
