package main

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
	services  []NPServiceMeta
	waitGroup sync.WaitGroup
}

type NeptuneService interface {
	Init(*NeptuneServerSkeleton) error
	Logic(NPServiceMeta) error
	Finish()
	Stop(NPServiceMeta)
}

func (s *NeptuneServerSkeleton) AddService(name string, service NeptuneService) {
	ctx, cancel := context.WithCancel(context.Background())
	newService := NPServiceMeta{
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
				log.Printf("service %s done\n", service.Name)
				s.waitGroup.Done()
			}()
			service.Service.Logic(service)
		}()
	}

	s.waitGroup.Wait()
	log.Printf("all services has finished, server will quit now.")
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

func (s MyService) Logic(service NPServiceMeta) error {
	fmt.Println("myservice logic")
	time.Sleep(time.Second * 3)
	return nil
}

func (s MyService) Finish() {
	fmt.Println("myservice finished")
}

func (s MyService) Stop(service NPServiceMeta) {
	fmt.Println("stoping myservice")
	service.Cancel()
}

func main() {
	server := &NeptuneServerSkeleton{}
	var service MyService
	server.AddService("foobar", service)
	server.Run()
}
