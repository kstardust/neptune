package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"math/rand"
	pb "neptune/src/proto"
	"time"

	"google.golang.org/grpc"
)

func client(playerId string) {
	rand.Seed(time.Now().Unix())

	conn, err := grpc.Dial(":5005", grpc.WithInsecure())
	if err != nil {
		log.Fatalf("cannot connect to server: %", err)
	}

	nclient := pb.NewNeptuneClient(conn)
	room, _ := nclient.CreateRoom(context.Background(), &pb.CreateRoomRequest{Num: 1})
	log.Printf("createroom: %v", room)

	resp1, _ := nclient.JoinRoom(context.Background(),
		&pb.JoinRoomRequest{PlayerId: playerId, RoomId: room.RoomId, Secret: room.Secret})
	log.Printf("joinroom: %v", resp1)

	client := pb.NewNeptuneClient(conn)
	stream, err := client.Stream(context.Background())

	if err != nil {
		log.Fatalf("open stream error", err)
	}

	ctx := stream.Context()

	done := make(chan bool)

	go func() {
		for i := 1; i <= 10; i++ {
			req := pb.StreamRequest{PlayerId: playerId, Payload: []byte(fmt.Sprintf("hello world %d", i))}

			if err := stream.Send(&req); err != nil {
				log.Fatalf("cannot send: %v", err)
			}

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
			log.Printf("%v received %v", playerId, resp)
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
	log.Printf("finished")
}

func main() {
	go client("player1")
	client("player2")
}
