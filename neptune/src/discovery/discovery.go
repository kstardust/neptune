package discovery

import (
	"fmt"
	"log"
	"neptune/src/skeleton"
	"time"
)

type Listener interface {
	Update(*DiscoveryServiceClient)
}

type DiscoveryServiceClient struct {
	listeners map[Listener]bool
	data      []string
}

func (c *DiscoveryServiceClient) Data() []string {
	return c.data
}

func (c *DiscoveryServiceClient) AddListener(listener Listener) {
	c.listeners[listener] = true
}

func (c *DiscoveryServiceClient) RemoveListener(listener Listener) {
	delete(c.listeners, listener)
}

func (c *DiscoveryServiceClient) update() {
	for l := range c.listeners {
		l.Update(c)
	}
}

func (c *DiscoveryServiceClient) Init(s *skeleton.NeptuneServerSkeleton) error {
	fmt.Println("Init discovery service client")
	return nil
}

func (c *DiscoveryServiceClient) Status() skeleton.NeptuneServiceStatus {
	return skeleton.NeptuneServiceNew
}

func (c *DiscoveryServiceClient) Logic(service *skeleton.NPServiceMeta) error {
	fmt.Println("Logic discovery service client")
	for {
		select {
		case <-service.Ctx.Done():
			log.Printf("discovery service was cancelled\n")
			return nil
		default:
		}

		time.Sleep(time.Second * 10)

		c.update()
	}
	return nil
}

func (c *DiscoveryServiceClient) Finish() {
	fmt.Println("Finish discovery service client")
}

func (c *DiscoveryServiceClient) Stop(service *skeleton.NPServiceMeta) {
	service.Cancel()
}

func main() {
	fmt.Println("hello world")
}
