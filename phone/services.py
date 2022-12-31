# import grpc
# from google.protobuf import empty_pb2
# from phone.serializers import UserProtoSerializer
# from django_grpc_framework.services import Service


# class UserService(Service):
#     def RegisterUser(self, request, context):
#         serializer = UserProtoSerializer(message=request)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return serializer.message


import grpc
import csv
from google.protobuf import empty_pb2
from phone.serializers import UserProtoSerializer
from django_grpc_framework.services import Service
from django.contrib.auth import get_user_model


User = get_user_model()


class UserService(Service):
    def RegisterUser(self, request, context):
        serializer = UserProtoSerializer(message=request)
        if serializer.is_valid():
            # check if user already exists
            if User.objects.filter(
                username=serializer.validated_data["username"]
            ).exists():
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("User already exists")
                return empty_pb2.Empty()

            # check if password is at least 8 characters long
            if len(serializer.validated_data["password"]) < 8:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Password must be at least 8 characters long")
                return empty_pb2.Empty()

            # save the user
            serializer.save()
            return serializer.message
        else:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(serializer.errors))
            return empty_pb2.Empty()


from django.core.files.storage import default_storage

# Get the file path of the uploaded file
# def read_csv_file(file):
#     file_path = default_storage.path(file.name)

#     with open(file_path, "r", encoding="utf-8") as f:
#         reader = csv.DictReader(f)
#         contents = [x for x in reader]
#     return contents


import os


def read_csv_file(file):
    # Save the uploaded file to a temporary directory
    file_path = default_storage.save("temp/{0}".format(file.name), file)

    # Open and read the file
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        contents = [x for x in reader]

    # Delete the temporary file
    os.remove(file_path)

    return contents
