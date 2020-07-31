package room

import (
	"testing"
)

func TestGenerateRoomId(t *testing.T) {
	for i := 0; i < 10; i++ {
		t.Log(generateRandomSeq(uint(i)))
	}
}

func TestNewRoom(t *testing.T) {
	for i := 0; i < 10; i++ {
		r, _ := New(nil)
		t.Logf("%+v", r)
		t.Log(r.Cap())
		t.Log(r.PlayerCnt())
	}
}
