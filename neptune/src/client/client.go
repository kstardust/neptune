package main

import (
	"context"
	"io"
	"log"
	"math/rand"
	pb "neptune/src/proto"
	"time"

	"google.golang.org/grpc"
)

func main() {
	rand.Seed(time.Now().Unix())

	conn, err := grpc.Dial(":5005", grpc.WithInsecure())
	if err != nil {
		log.Fatalf("cannot connect to server: %", err)
	}

	nclient := pb.NewNeptuneClient(conn)
	room, _ := nclient.CreateRoom(context.Background(), &pb.CreateRoomRequest{Num: 1})
	log.Printf("createroom: %v", room)

	resp1, _ := nclient.JoinRoom(context.Background(), &pb.JoinRoomRequest{RoomId: room.RoomId, Secret: room.Secret})
	log.Printf("joinroom: %v", resp1)

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
