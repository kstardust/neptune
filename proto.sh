python -m grpc_tools.protoc -I./common_proto --python_out=neptune_py/proto --grpc_python_out=neptune_py/proto common_proto/*.proto
cd neptune && protoc -I src/proto src/proto/*.proto --go_out=plugins=grpc:src/proto
