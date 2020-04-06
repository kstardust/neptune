package hub

import (
	"crypto/rand"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"time"
)

type DockId string
type PortId uint64

// copied from internet
// https://play.golang.org/p/4FkNSiUDMg
func NewUUID() (string, error) {
	uuid := make([]byte, 16)
	n, err := io.ReadFull(rand.Reader, uuid)
	if n != len(uuid) || err != nil {
		return "", err
	}
	// variant bits; see section 4.1.1
	uuid[8] = uuid[8]&^0xc0 | 0x80
	// version 4 (pseudo-random); see section 4.1.3
	uuid[6] = uuid[6]&^0xf0 | 0x40
	return fmt.Sprintf("%x-%x-%x-%x-%x", uuid[0:4], uuid[4:6], uuid[6:8], uuid[8:10], uuid[10:]), nil
}

type Aircraft interface {
	DeliveryCargo(data []byte) error
	Detach()
}

type Cargo struct {
	Frame      uint64
	Containers []Container
}

type Container struct {
	Id      uint64
	Time    int64
	Payload []byte
}

type Dock struct {
	fps        int64
	ships      int64
	arrivals   int64
	dockId     DockId
	cargoId    uint64
	portId     PortId
	frame      uint64
	lastFrame  time.Time
	ShouldStop bool

	cargo Cargo
	ports map[PortId]Aircraft
	Crane chan []byte
}

func (cr *Dock) Port(ship Aircraft) (PortId, error) {
	if cr.isReady() {
		return PortId(0), fmt.Errorf("Dock is full")
	}
	cr.arrivals++
	cr.portId++
	cr.ports[cr.portId] = ship
	return cr.portId, nil
}

func (cr *Dock) Detach(pid PortId) {
	cr.arrivals--
	delete(cr.ports, pid)
}

func (cr *Dock) Delivery() {
	// never do any heavy work in this function, otherwise there will be
	// no opportunities for others to run.
	if !cr.isReady() {
		return
	}

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

	if !cr.isReady() {
		return
	}

	container := Container{}
	cr.cargoId++
	container.Id = cr.cargoId
	container.Payload = data
	container.Time = time.Since(cr.lastFrame).Nanoseconds()
	cr.cargo.Containers = append(cr.cargo.Containers, container)
}

func (cr *Dock) stop() {
	log.Println("stop ", cr.dockId)
}

func (cr *Dock) isReady() bool {
	log.Println(cr.arrivals, cr.ships)
	return cr.arrivals == cr.ships
}

func (cr *Dock) SetTheBallRolling() {
	if cr.ports == nil {
		cr.ports = make(map[PortId]Aircraft)
	}

	if cr.Crane == nil {
		cr.Crane = make(chan []byte)
	}

	if cr.frame != 0 {
		return
	}
	ticker := time.NewTicker(time.Second / time.Duration(cr.fps))

	// preallocate some space
	cr.cargo.Containers = make([]Container, 0, 50)

	cr.lastFrame = time.Now()
	// delivery has the frist priority
	for {
		if cr.ShouldStop {
			// should close all connections here
			cr.stop()
			return
		}

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
