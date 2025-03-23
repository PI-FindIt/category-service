import protobuf.service_name.kebab_pb2 as _service_name_pb2
import protobuf.service_name.kebab_pb2_grpc as _service_name_pb2_grpc

_service_name_channel = grpc.aio.insecure_channel("service-name:50051")
service_name_stub = _service_name_pb2_grpc.ServiceNameStub(_service_name_channel)
service_name_servicer = _service_name_pb2_grpc.ServiceNameServicer()
service_name_models = _service_name_pb2
