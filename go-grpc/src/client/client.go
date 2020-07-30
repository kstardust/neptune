package main

import (
	"context"
	pb "go-grpc/src/proto"
	"io"
	"log"
	"math/rand"
	"time"

	"google.golang.org/grpc"
)

func main() {
	rand.Seed(time.Now().Unix())

	conn, err := grpc.Dial(":5005", grpc.WithInsecure())
	if err != nil {
		log.Fatalf("cannot connect to server: %", err)
	}

	client := pb.NewMathClient(conn)
	stream, err := client.Max(context.Background())

	if err != nil {
		log.Fatalf("open stream error", err)
	}

	var max int32
	ctx := stream.Context()

	done := make(chan bool)

	go func() {
		for i := 1; i <= 10; i++ {
			rnd := int32(rand.Intn(i))
			req := pb.Request{Num: rnd}

			if err := stream.Send(&req); err != nil {
				log.Fatalf("cannot send: %v", err)
			}
			log.Printf("%d send", req.Num)
			time.Sleep(time.Millisecond * 200)
		}

		if err := stream.CloseSend(); err != nil {
			log.Println(err)
		}
 	}()

	go func() {
		for {
			resp, err := stream.Recv()
			if err == io.EOF {
				close(done)
				return
			}
			if err != nil {
				log.Fatal("cannot receive: %v", err)
			}
			max = resp.Result
			log.Println("new max %d received", max)
		}
	}()

	go func() {
		<-ctx.Done()
		if err := ctx.Err(); err != nil {
			log.Println(err)
		}
		close(done)
	}()

	<-done
	log.Printf("finished with max=%d", max)
}
