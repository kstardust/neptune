package hub

import (
	"log"
)

type Hub struct {
	Docks map[DockId]*Dock
}

func NewHub() *Hub {
	return &Hub{Docks: make(map[DockId]*Dock)}
}

func (h *Hub) FreeDock(id DockId) {
	dock, ok := h.Docks[id]
	if ok {
		dock.ShouldStop = true
		delete(h.Docks, id)
	}
}

func (h *Hub) NewDock(ships int64, fps int64) (*Dock, DockId) {
	uuid, error := NewUUID()
	if error != nil {
		log.Println("error cannot generate uuid", error)
		return nil, ""
	}
	dockId := DockId(uuid)
	dock := &Dock{dockId: dockId, fps: fps, ships: ships}
	h.Docks[dockId] = dock
	return dock, dockId
}
