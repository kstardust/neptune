package logic

import (
	"log"
	"neptune/src/room"
)

func Logic(r *room.Room) error {
	log.Printf("start run game logic in room: %s", r.Id)
	for {
		select {
		case <-r.Ctx.Done():
			return r.Ctx.Err()
		default:
		}

		select {
		case req := <-r.GetInput():
			for _, p := range r.Players {
				p.SendMessage(req.GetPayload())
			}
			log.Printf("input: %v", req)
		}

		return nil
	}
}
