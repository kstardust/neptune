package room

import (
	"log"
	pb "neptune/src/proto"
)

type PlayerStatus int
type PlayerId string

const (
	PlayerStatusDisconnect PlayerStatus = iota
	PlayerStatusConnected
	PlayerStatusStreaming
)

type Player interface {
	SendMessage(msg []byte) error
	Kill()

	SetId(s PlayerId)
	Id() PlayerId

	SetStatus(PlayerStatus)
	Status() PlayerStatus

	Room() RoomId
	SetRoom(r RoomId)

	SetRpcBackend(pb.Neptune_StreamServer)
	RpcBackend() pb.Neptune_StreamServer
}

type BasicPlayer struct {
	status PlayerStatus
	id     PlayerId
	roomId RoomId
	rpc    pb.Neptune_StreamServer
}

func NewPlayer(id PlayerId) Player {
	p := new(BasicPlayer)
	p.id = id
	p.status = PlayerStatusDisconnect
	return p
}

func (p *BasicPlayer) SetRpcBackend(rpc pb.Neptune_StreamServer) {
	p.rpc = rpc
}

func (p *BasicPlayer) RpcBackend() pb.Neptune_StreamServer {
	return p.rpc
}

func (p *BasicPlayer) SetStatus(status PlayerStatus) {
	p.status = status
}

func (p *BasicPlayer) Status() PlayerStatus {
	return p.status
}

func (p *BasicPlayer) SetRoom(r RoomId) {
	p.roomId = r
}

func (p *BasicPlayer) Room() RoomId {
	return p.roomId
}

func (p *BasicPlayer) SendMessage(msg []byte) error {
	if p.Status() != PlayerStatusStreaming {
		log.Printf("player [%s] is not streaming", p.Id())
		return nil
	}

	resp := &pb.StreamResponse{
		Payload: msg,
	}
	return p.RpcBackend().Send(resp)
}

func (p *BasicPlayer) Kill() {
}

func (p *BasicPlayer) Id() PlayerId {
	return p.id
}

func (p *BasicPlayer) SetId(id PlayerId) {
	p.id = id
}
