from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, format_lazy
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView, CreateAPIView
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login

from django.contrib.auth import get_user_model
from .serializers import (
    UserRegisterSerializer,
    UsersListSerializer,
    LoginSerializer,
    UserProtoSerializer,
    StrokeDataUploadSerializer,
)
from .models import EmailPhoneUser, Device
from .utils import *
from .mixins import *
from .parsers import *
from django.utils import timezone
from django.contrib import messages
from .models import Subscriber
from django.db import IntegrityError
from .tasks import async_send_newsletter
from django.shortcuts import redirect
from .mixins import DeviceMixin, LoginThrottlingMixin
import requests
from .forms import WordForm

# Create your views here.


class UsersListView(ListAPIView):
    permission_classes = [
        AllowAny,
    ]
    serializer_class = UsersListSerializer
    queryset = get_user_model().objects.all()

    def get(self, request):
        users = get_user_model().objects.all()
        serializer = UsersListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


M3O_API_TOKEN = "ODU3MzFmN2ItNjM3Ny00Y2MzLWEzNjktMjMxNGE5MjU1MmZl"

url = "https://api.m3o.com/v1/user/Create"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {M3O_API_TOKEN}",
}


class UserRegisterView(APIView):
    permission_classes = [
        AllowAny,
    ]
    serializer_class = UserRegisterSerializer
    queryset = get_user_model().objects.all()

    def perform_create(self, serializer):
        return serializer.save()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = self.perform_create(serializer)
            user.set_password(request.POST.get("password"))

            # add tokens
            refresh = RefreshToken.for_user(user)
            res = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }

            data = {
                "email": f'{serializer.validated_data["username"]}',
                "id": f"{user.id}",
                "password": f'{request.POST.get("password")}',
                "username": f'{serializer.validated_data["username"]}',
            }
            response = requests.post(url, headers=headers, json=data)
            print(response.status_code)
            print(response.json())
            print(data)

            return Response(res, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [
        AllowAny,
    ]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            context={"request": request}, data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data["username"]
            password = request.POST.get("password")

            user_login = authenticate(
                username=username,
                password=password,
                backend="phone.authenticate.EmailModelBackend",
            ) or authenticate(
                username=username,
                password=password,
                backend="phone.authenticate.PhoneModelBackend",
            )

            refresh = RefreshToken.for_user(user_login)
            ip_address = get_ip_address(request)
            device_name, device_details = get_device_details(
                request.META, str(refresh.access_token)
            )
            device = Device.objects.create(
                user=user_login,
                last_request_datetime=timezone.now(),
                name=device_name,
                details=device_details,
                permanent_token=refresh,
                ip_address=ip_address,
            )
            device.save()

            auth_login(request, user_login)
            user = get_user_model().objects.get(username=username)
            user_device = Device.objects.filter(user=user).first()
            # print(user.device)
            if (
                user_device.ip_address != ip_address
                or user_device.device.name != device_name
            ):
                warning_mail_send(username, ip_address)

            res = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            return Response(res, status=status.HTTP_200_OK)


# Login with Mixin


class LoginView2(APIView, DeviceMixin):
    permission_classes = [
        AllowAny,
    ]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            context={"request": request}, data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data["username"]
            password = request.POST.get("password")

            user_login = authenticate(
                username=username,
                password=password,
                backend="phone.authenticate.EmailModelBackend",
            ) or authenticate(
                username=username,
                password=password,
                backend="phone.authenticate.PhoneModelBackend",
            )

            refresh = RefreshToken.for_user(user_login)

            res = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            return Response(res, status=status.HTTP_200_OK)


def subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email")
        subscriber = Subscriber(email=email, confirmed=True)
        if subscriber == Subscriber.objects.filter(email=subscriber.email):
            messages.error(request, "You are already subscribed to our newsletter!")
            return redirect("login")
        else:
            try:
                subscriber.save()
                async_send_newsletter.delay()
                messages.success(request, "You have been subscribed to our newsletter!")
                return redirect("login")
            except IntegrityError as e:
                messages.error(request, "You are already subscribed to our newsletter!")
                return redirect("login")
    else:
        return redirect("login")


def unsubscribe(request):
    confirme_subscribers = Subscriber.objects.get(email=request.GET["email"])
    for subscriber in confirme_subscribers:
        subscriber.delete()
        messages.success(
            request, "You have successfully unsubscribed from our newsletter!"
        )
        return redirect("login")


from django.conf import settings
from django.shortcuts import render


def get_definition(request):
    if request.method == "POST":
        form = WordForm(request.POST)
        if form.is_valid():
            api_key = settings.DICTIONARY_KEY
            endpoint = "https://www.dictionaryapi.com/api/v3/references/thesaurus/json/"
            word = form.cleaned_data["input"]
            url = f"{endpoint}{word}?key={api_key}"
            response = requests.get(url)
            data = response.json()
            # data = JsonResponse(response, safe=False)
            synonyms = data[0]["meta"]["syns"][0]
            meaning = data[0]["shortdef"][0]
            return render(
                request,
                "dictionary.html",
                {"synonyms": synonyms, "meaning": meaning, "word": word},
            )
    else:
        form = WordForm()
    return render(request, "dictionary.html", {"form": form})


# https://www.dictionaryapi.com/api/v3/references/thesaurus/json/test?key=15b1025e-5041-4d7b-9f7b-4f74bd0deabe


from .models import Notification


def notifications(request):
    if request.method == "POST":
        # Create a new notification object
        title = request.POST.get("title")
        body = request.POST.get("body")
        notification = Notification.objects.create(title=title, body=body)
        notification.save()

    # Get all notification objects
    notifications = Notification.objects.all()
    return render(request, "index.html", {"notifications": notifications})


# class StrokeDataUpload(APIView, DataValidationMixin):
#     permission_classes = [
#         AllowAny,
#     ]
#     parser_classes = [WordParser, PDFParser, JSONParser, CSVParser, ExcelParser]
#     serializer_class = StrokeDataUploadSerializer

#     def post(self, request):
#         # Create a serializer instance with the request data
#         serializer = StrokeDataUploadSerializer(data=request.FILES)
#         # Validate the serializer
#         serializer.is_valid(raise_exception=True)
#         # Parse the file using the `parse` method of the FileTypeMixin
#         data = self.parse(serializer.validated_data["stroke"], request.content_type)
#         # Validate the data using the DataValidationMixin
#         self.validate_data(data)
#         # Save the serializer data to the Stroke model
#         # Stroke.objects.create(**data)
#         print("data", data)

#         return Response(
#             {"msg": "Stroke data uploaded successfully"}, status=status.HTTP_201_CREATED
#         )

# from rest_framework.parsers import FileUploadParser
from rest_framework import generics


class StrokeDataUpload(generics.CreateAPIView):
    serializer_class = StrokeDataUploadSerializer
    # parser_classes = [FileUploadParser]

    parser_classes = [WordParser, PDFParser, JSONParser, CSVParser, ExcelParser]

    def post(self, request, filename, format=None, *args, **kwargs):
        print(request.data)
        serializer = self.serializer_class(data=request.FILES)
        if serializer.is_valid():
            stroke = serializer.validated_data["stroke"]
            print(str(stroke))
            print(request.content_type)
            # Do something with the uploaded file
            return Response(status=200)


from rest_framework import generics


# class FileUploadView(DataValidationMixin, generics.CreateAPIView):
#     serializer_class = StrokeDataUploadSerializer
#     content_type_whitelist = [
#         "text/csv",
#         "application/json",
#         "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
#         "application/pdf",
#         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#     ]

#     def post(self, request, format=None, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         uploaded_file = request.FILES["stroke"]
#         content_type = uploaded_file.content_type
#         print("content_type", content_type)
#         if content_type not in self.content_type_whitelist:
#             return Response(
#                 {"error": "Invalid file type"}, status=status.HTTP_400_BAD_REQUEST
#             )

#         print("uploaded_file", uploaded_file)
#         if content_type == "text/csv":
#             import csv

#             with open(uploaded_file.name, "r", encoding="utf-8") as f:
#                 reader = csv.DictReader(f)
#                 contents = [x for x in reader]

#                 self.validate_data(request, data=contents[0].keys())

#         if (
#             content_type
#             == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         ):
#             import openpyxl

#             workbook = openpyxl.load_workbook(uploaded_file.name)
#             sheet_names = workbook.sheetnames
#             sheet = workbook[sheet_names[0]]
#             # Print the sheet data
#             for row in sheet.rows:
#                 for cell in row:
#                     print(cell.value)

#         if (
#             content_type
#             == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
#         ):
#             import docx

#             document = docx.Document(uploaded_file.name)
#             print(document.paragraphs[0].text)

#         # Now you can use the file as needed, such as by saving it to a database or storing it on a file system.

#         return Response(
#             {"message": "Saved successfully"}, status=status.HTTP_201_CREATED
#         )

from .models import Stroke


class FileUploadView(DataValidationMixin, generics.CreateAPIView):
    serializer_class = StrokeDataUploadSerializer
    content_type_whitelist = [
        "text/csv",
        "application/json",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ]

    def post(self, request, format=None, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        uploaded_file = request.FILES["stroke"]
        file_name = uploaded_file.name
        content_type = uploaded_file.content_type
        if content_type not in self.content_type_whitelist:
            return Response(
                {"error": "Invalid file type"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            if content_type == "text/csv":
                import csv

                with open(uploaded_file.name, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    contents = [x for x in reader]
                    self.validate_data(request, data=contents[0].keys())
                    # print("contents", contents[0])
                    # Create a new Stroke instance with the data in the row
                    stroke = Stroke(
                        user=request.user,
                        glucose_level=contents[0]["glucose_level"],
                        bmi=contents[0]["bmi"],
                        blood_pressure_systolic=contents[0]["blood_pressure_systolic"],
                        blood_pressure_diastolic=contents[0][
                            "blood_pressure_diastolic"
                        ],
                        age=contents[0]["age"],
                    )
                    stroke.save()
                    # stroke = Stroke(
                    #     user=request.user,
                    #     glucose_level=row["glucose_level"],
                    #     bmi=row["bmi"],
                    #     blood_pressure_systolic=row["blood_pressure_systolic"],
                    #     blood_pressure_diastolic=row["blood_pressure_diastolic"],
                    #     age=row["age"],
                    # )
                    # stroke.save()
                    print("saving stroke data")
            if (
                content_type
                == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ):
                import openpyxl

                workbook = openpyxl.load_workbook(uploaded_file.name)
                sheet_names = workbook.sheetnames
                sheet = workbook[sheet_names[0]]
            if (
                content_type
                == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ):
                import docx

                document = docx.Document(uploaded_file.name)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"message": "Saved successfully"}, status=status.HTTP_201_CREATED
        )
