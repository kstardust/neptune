package hub

import (
	"encoding/json"
	"log"
	"time"
)

type PortId int

type Aircraft interface {
	DeliveryCargo(data []byte) error
	Detach()
}

type Cargo struct {
	Frame      uint64
	Containers []Container
}

type Container struct {
	Id      int
	Time    int64
	Payload []byte
}

type Dock struct {
	cargoId   int
	portId    PortId
	frame     uint64
	lastFrame time.Time

	cargo Cargo
	ports map[PortId]Aircraft
	Crane chan []byte
}

func (cr *Dock) Port(ship Aircraft) PortId {
	cr.portId++
	cr.ports[cr.portId] = ship
	return cr.portId
}

func (cr *Dock) Detach(pid PortId) {
	delete(cr.ports, pid)
}

func (cr *Dock) Delivery() {
	// never do any heavy work in this function, otherwise there will be
	// no opportunities for others to run.

	cr.cargo.Frame = cr.frame
	cargo, error := json.Marshal(cr.cargo)
	if error != nil {
		log.Fatalln("json Marshal", error)
	}

	for pid, ac := range cr.ports {
		if error := ac.DeliveryCargo(cargo); error != nil {
			log.Println("delivery error: ", ac, error)
			cr.Detach(pid)
			ac.Detach()
		}
	}

	// discard cargo but not release them(i.e. doesnt trigger garbage collection)
	cr.cargo.Containers = cr.cargo.Containers[:0]
	now := time.Now()
	cr.frame++
	log.Println(cr.frame, now.Sub(cr.lastFrame))
	cr.lastFrame = now
}

func (cr *Dock) LoadCargo(data []byte) {
	container := Container{}
	cr.cargoId++
	container.Id = cr.cargoId
	container.Payload = data
	container.Time = time.Since(cr.lastFrame).Nanoseconds()
	cr.cargo.Containers = append(cr.cargo.Containers, container)
}

func (cr *Dock) SetTheBallRolling(fps int64) {
	if cr.ports == nil {
		cr.ports = make(map[PortId]Aircraft)
	}

	if cr.Crane == nil {
		cr.Crane = make(chan []byte)
	}

	if cr.frame != 0 {
		return
	}
	ticker := time.NewTicker(time.Second / time.Duration(fps))

	// preallocate some space
	cr.cargo.Containers = make([]Container, 0, 50)

	cr.lastFrame = time.Now()
	// delivery has the frist priority
	for {
		select {
		case <-ticker.C:
			cr.Delivery()
			continue
		default:
		}

		select {
		case <-ticker.C:
			cr.Delivery()
			continue
		case payload := <-cr.Crane:
			cr.LoadCargo(payload)
		}
	}
}
