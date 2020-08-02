package room

type PlayerStatus int
type PlayerId string

const (
	PlayerStatusDisconnect PlayerStatus = iota
	PlayerStatusConnected
	PlayerStatusStreaming
)

type Player interface {
	SendMessage(msg []byte) error
	SetId(s PlayerId)
	Id() PlayerId
	Room() RoomId
	SetRoom(r RoomId)
	Kill()
}

type BasicPlayer struct {
	status PlayerStatus
	id     PlayerId
	roomId RoomId
}

func NewBasicPlayer(id PlayerId) Player {
	p := new(BasicPlayer)
	p.id = id
	p.status = PlayerStatusDisconnect
	return p
}

func (p *BasicPlayer) SetRoom(r RoomId) {
	p.roomId = r
}

func (p *BasicPlayer) Room() RoomId {
	return p.roomId
}

func (p *BasicPlayer) SendMessage(msg []byte) error {
	return nil
}

func (p *BasicPlayer) Kill() {
}

func (p *BasicPlayer) Id() PlayerId {
	return p.id
}

func (p *BasicPlayer) SetId(id PlayerId) {
	p.id = id
}
