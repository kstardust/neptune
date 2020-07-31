package room

import (
	"math/rand"
	"neptune/src/player"
)

type RoomId string
type GameLogic = func(room *Room) error

type Room struct {
	Id        RoomId
	Players   []*player.Player
	gameLogic GameLogic
	Secret    string
}

var Letters = []rune("abcdefghijklmnopqrstuvwxyz0123456789")

func generateRandomSeq(length uint) string {
	res := make([]rune, length)
	for i := range res {
		res[i] = Letters[rand.Intn(len(Letters))]
	}
	return string(res)
}

func newRoom(players uint, roomIdlength uint, logic GameLogic) (*Room, error) {
	room := new(Room)
	room.Id = RoomId(generateRandomSeq(4))
	room.Players = make([]*player.Player, 0, players)
	room.gameLogic = logic
	room.Secret = generateRandomSeq(12)
	return room, nil
}

func (r *Room) Cap() int {
	return cap(r.Players)
}

func (r *Room) PlayerCnt() int {
	return len(r.Players)
}

func (r *Room) PlayerJoin(p *player.Player) error {
	return nil
}

func joinRoom(RoomId) {
}

func New(logic GameLogic) (*Room, error) {
	return newRoom(2, 4, nil)
}
