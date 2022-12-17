# import grpc
# from user_proto import user_pb2, user_pb2_grpc

# with grpc.insecure_channel("localhost:50051") as channel:
#     stub = user_pb2_grpc.UserServiceStub(channel)
#     user_data = {
#         "username": "grpc@gmail.com",
#         "password": "@Test1234"
#     }
#     response = stub.RegisterUser(user_data)
#     print(response, end="")


import grpc
from user_proto import user_pb2, user_pb2_grpc

with grpc.insecure_channel("localhost:50051") as channel:
    stub = user_pb2_grpc.UserServiceStub(channel)
    user_data = {
        "username": "grpc3@gmail.com",
        "password": "@Test1234"
    }
    user = user_pb2.User(username=user_data['username'], password=user_data['password'])
    response = stub.RegisterUser(user)
    # print(user, end="")
    print(response, end="")
