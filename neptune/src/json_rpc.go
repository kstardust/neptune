// a very primitive json-rpc implementation using reflection

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"reflect"
)

type JsonRpc struct {
	MethodName string
	Args      [][]byte
}

type TestRpcEntity int

func (*TestRpcEntity) RpcFoobar(arg1 int, arg2 string) {
	fmt.Printf("-----%v %v\n", arg1, arg2)
}

type RpcSlot struct {
	entity interface{}
}

func (s *RpcSlot) RpcSlotRegister(e interface{}) {
	s.entity = e
}

func (s *RpcSlot) Invoke(data []byte) error {
	rpc := new(JsonRpc)
	if err := json.Unmarshal(data, rpc); err != nil {
		return fmt.Errorf("cannot decode data: %v", err)
	}

	method := reflect.ValueOf(s.entity).MethodByName(rpc.MethodName)

	if method == (reflect.Value{}) {
		return fmt.Errorf("no such method %v", rpc.MethodName)
	}

	numArgs := method.Type().NumIn()
	if len(rpc.Args) != numArgs {
		return fmt.Errorf("arg num not match, expect: %v actual: %v", numArgs, len(rpc.Args))
	}

	args := make([]reflect.Value, numArgs)

	for i := 0; i < numArgs; i++ {
		v := reflect.New(method.Type().In(i))
		fmt.Println(v, reflect.ValueOf(v), reflect.ValueOf(v.Interface()))
		if err := json.Unmarshal(rpc.Args[i], v.Interface()); err != nil {
			return fmt.Errorf("cannot decode arg: %v", err)
		}
		args[i] = v.Elem()
	}

	method.Call(args)
	return nil
}

func (*RpcSlot) EncodeCall(method string, args ...interface{}) ([]byte, error) {
	rpc := JsonRpc{}
	rpc.MethodName = method
	rpc.Args = make([][]byte, len(args))
	for i := range rpc.Args {
		if data, err := json.Marshal(args[i]); err != nil {
			return nil, fmt.Errorf("Rpc Call failed: %v", err)
		} else {
			rpc.Args[i] = data
		}
	}

	data, err := json.Marshal(rpc)
	if err != nil {
		return nil, fmt.Errorf("Rpc Call failed: %v", err)
	}

	return data, nil
}

func main() {
	var t TestRpcEntity
	var slot RpcSlot
	slot.RpcSlotRegister(&t)
	d, _ := slot.EncodeCall("RpcFoobar", 1, "string")

	fmt.Printf("%s", d)

	if err := slot.Invoke(d); err != nil {
		log.Println(err)
	}
}
