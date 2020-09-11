package skeleton

import (
	"context"
	"fmt"
	"log"
	"sync"
	"time"
)

type NPServiceMeta struct {
	Service NeptuneService
	Ctx     context.Context
	Name    string
	Server  *NeptuneServerSkeleton
	Cancel  context.CancelFunc
}

type NeptuneServerSkeleton struct {
	services  []*NPServiceMeta
	waitGroup sync.WaitGroup
}

type NeptuneServiceStatus int

const (
	NeptuneServiceNew NeptuneServiceStatus = iota
	NeptuneServiceInited
	NeptuneServiceRunnning
	NeptuneServiceFinished
)

type NeptuneService interface {
	Init(*NeptuneServerSkeleton) error
	Logic(*NPServiceMeta) error
	Status() NeptuneServiceStatus
	Finish()
	Stop(*NPServiceMeta)
}

func (s *NeptuneServerSkeleton) AddService(name string, service NeptuneService) {
	ctx, cancel := context.WithCancel(context.Background())
	newService := &NPServiceMeta{
		Service: service,
		Name:    name,
		Ctx:     ctx,
		Server:  s,
		Cancel:  cancel,
	}

	s.services = append(s.services, newService)
}

func (s *NeptuneServerSkeleton) InitServices() {
	for _, service := range s.services {
		if service.Service.Status() != NeptuneServiceNew {
			log.Printf("cannot init service %s in status %v\n", service.Name, service.Service.Status())
			continue
		}
		if err := service.Service.Init(s); err != nil {
			log.Fatalf("error occurred during init %v\n", err)
		}
	}
}

func (s *NeptuneServerSkeleton) Run() {
	s.InitServices()
	log.Println("start running server")
	for _, service := range s.services {
		service := service // capture service
		s.waitGroup.Add(1)
		go func() {
			defer func() {
				service.Service.Finish()
				log.Printf("service %s has exited.\n", service.Name)
				s.waitGroup.Done()
			}()
			service.Service.Logic(service)
		}()
	}

	s.waitGroup.Wait()
	log.Printf("all services have finished, server will quit now.")
}

func (s *NeptuneServerSkeleton) FindService(name string) NeptuneService {
	for _, service := range s.services {
		if service.Name == name {
			return service.Service
		}
	}
	return nil
}

func (s *NeptuneServerSkeleton) CancelAll() {
	for _, service := range s.services {
		service.Service.Stop(service)
	}
}

type MyService int

func (s MyService) Init(ns *NeptuneServerSkeleton) error {
	fmt.Println("myservice init")
	return nil
}

func (s MyService) Logic(service *NPServiceMeta) error {
	fmt.Println("myservice logic")
	time.Sleep(time.Second * 3)
	return nil
}

func (s MyService) Status() NeptuneServiceStatus {
	return NeptuneServiceNew
}

func (s MyService) Finish() {
	fmt.Println("myservice finished")
}

func (s MyService) Stop(service *NPServiceMeta) {
	fmt.Println("stoping myservice")
	service.Cancel()
}
