from rest_framework.views import APIView, View
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
from .services import *
from django.utils import timezone
from django.contrib import messages
from .models import Subscriber
from django.db import IntegrityError
from .tasks import async_send_newsletter
from django.shortcuts import redirect
from .mixins import DeviceMixin, LoginThrottlingMixin
import requests
from .forms import WordForm
from django.core.files.storage import default_storage

# Create your views here.


# Magic Link
from django.conf import settings
import jwt
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from .forms import SignUpForm
from django.urls import reverse


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
                # import csv

                # with open(uploaded_file.name, "r", encoding="utf-8") as f:
                #     reader = csv.DictReader(f)
                #     contents = [x for x in reader]
                contents = read_csv_file(uploaded_file)
                self.validate_data(request, data=contents[0].keys())
                # print("contents", contents[0])
                # Create a new Stroke instance with the data in the row
                # default_storage.save(
                #     "users_uploaded_files/{0}/{1}".format(
                #         request.user.username, file_name
                #     )
                # )

                stroke = Stroke(
                    user=request.user,
                    glucose_level=contents[0]["glucose_level"],
                    bmi=contents[0]["bmi"],
                    blood_pressure_systolic=contents[0]["blood_pressure_systolic"],
                    blood_pressure_diastolic=contents[0]["blood_pressure_diastolic"],
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


# views.py
from django.http import HttpResponse
import datetime


def time(request):
    now = datetime.datetime.now()
    return HttpResponse(now.strftime("%Y-%m-%d %H:%M:%S"))


from django.shortcuts import render

time = 0


def time_view(request):
    global time
    context = {"time": time}
    return render(request, "time.html", context)


def start_view(request):
    global time
    if request.method == "POST":
        # process form data
        time += 1
        context = {"time": time}
        return render(request, "time.html", context)
    else:
        # render the form template
        return render(request, "start.html")


def reset_view(request):
    global time
    if request.method == "POST":
        # process form data
        time = 0
        context = {"time": time}
        return render(request, "time.html", context)
    else:
        # render the form template
        return render(request, "reset.html")


from django.shortcuts import render
import datetime
from django.views.decorators.csrf import csrf_exempt


def counter(request):
    current_time = datetime.datetime.now()
    return render(request, "counter.html", {"current_time": current_time})


@csrf_exempt
def stop(request):
    return render(request, "counter.html", {"current_time": None})


# @csrf_exempt
# def stopwatch(request):
#     elapsed_time = 0  # replace this with the elapsed time from the database
#     return render(request, 'stopwatch.html', {'elapsed_time': elapsed_time})


import random


@csrf_exempt
def stopwatch(request):
    elapsed_time = 0  # replace this with the elapsed time from the database
    # Select a random picture from a list of picture URLs
    picture_urls = [
        "https://picsum.photos/200/300",
        "https://picsum.photos/200/301",
        "https://picsum.photos/200/302",
        "https://picsum.photos/200/303",
    ]
    random_picture_url = random.choice(picture_urls)
    return render(
        request,
        "stopwatch.html",
        {"elapsed_time": elapsed_time, "random_picture_url": random_picture_url},
    )


from .serializers import SubscriptionSerializer
from .models import Subscription


class CreateSubscriptionView(generics.CreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer


from django.http import JsonResponse


class PaymentWebhookView(View):
    def post(self, request):
        # Extract the payment information from the request
        payment_info = request.POST.get("payment_info")

        # Use the payment information to create or update a subscription
        subscription = process_payment(payment_info)

        return JsonResponse({"status": "success"})


def process_payment(payment_info):
    # Extract necessary information from the payment_info
    subscription_id = payment_info["subscription_id"]
    amount = payment_info["amount"]
    start_date = payment_info["start_date"]
    end_date = payment_info["end_date"]
    frequency = payment_info["frequency"]
    next_delivery_date = payment_info["next_delivery_date"]

    try:
        # check if a subscription with the given id already exists
        subscription = Subscription.objects.get(id=subscription_id)
        # Update the subscription based on the payment information
        subscription.amount = amount
        subscription.status = status
        subscription.save()
        return subscription
    except Subscription.DoesNotExist:
        # Create a new subscription
        subscription = Subscription.objects.create(
            id=subscription_id,
            amount=amount,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            next_delivery_date=next_delivery_date,
        )
        return subscription


from django.shortcuts import render
import requests


def search_movie(request):
    if request.method == "POST":
        movie_title = request.POST["movie_title"]
        api = "6e907d6d"
        url = f"http://www.omdbapi.com/?apikey={api}&t={movie_title}"
        response = requests.get(url)
        data = response.json()
        title = data["Title"]
        year = data["Year"]
        rating = data["Ratings"][0]["Value"]
        release_date = data["Released"]
        language = data["Language"]
        poster = data["Poster"]

        movie = {
            "Title": title,
            "Year": year,
            "Rating": rating,
            "Released": release_date,
            "Language": language,
            "Poster": poster,
        }
        print(movie)
        return render(request, "start.html", {"movies": movie})
    else:
        return render(request, "start.html")


# views.py
from django.shortcuts import render
from .forms import Page1Form, Page2Form, Page3Form


def forms(request):
    if request.method == "POST":
        if "page1" in request.POST:
            form = Page2Form()
            return render(request, "page2.html", {"form": form})
        elif "page2" in request.POST:
            form = Page3Form()
            return render(request, "page3.html", {"form": form})
        else:
            # save the form data
            # ...
            return render(request, "completed.html")
    else:
        form = Page1Form()
    return render(request, "forms.html", {"form": form})


from .forms import MoveForm


def make_move(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    board = [list(row) for row in game.board.split("-")]
    player = game.next_player
    form = MoveForm(request.POST or None, board=board)
    if form.is_valid():
        row = form.cleaned_data["row"]
        col = form.cleaned_data["col"]
        board[row][col] = player.symbol
        game.board = "-".join("".join(row) for row in board)
        game.next_player = game.other_player
        if game.is_finished():
            game.winner = player
            game.finished = True
        game.save()
        return redirect("game_detail", game_id=game.id)
    return render(request, "game_detail.html", {"game": game, "form": form})


from django.shortcuts import render, get_object_or_404
from .models import Game, Player


def game_detail(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    return render(request, "game_detail.html", {"game": game})


def game_list(request):
    games = Game.objects.all()
    return render(request, "game_list.html", {"games": games})


def player_detail(request, player_id):
    player = get_object_or_404(Player, pk=player_id)
    return render(request, "player_detail.html", {"player": player})


def player_list(request):
    players = Player.objects.all()
    return render(request, "player_list.html", {"players": players})


from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail

from .serializers import PasswordResetSerializer, PasswordResetConfirmSerializer


class PasswordResetView(GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = get_user_model().objects.get(email=email)
        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        password_reset_url = f"{current_site}/password-reset-confirm/{uid}/{token}"
        email_subject = "Password Reset Request"
        email_body = (
            f"Please follow the link to reset your password: {password_reset_url}"
        )
        send_mail(
            email_subject, email_body, "from@example.com", [email], fail_silently=False
        )
        return Response({"email": email}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(
                {"status": "password reset successful"}, status=status.HTTP_200_OK
            )
        return Response(
            {"status": "password reset failed"}, status=status.HTTP_400_BAD_REQUEST
        )


from django.http import JsonResponse
from .models import DataPoint

def get_data(request):
    data = list(DataPoint.objects.values('value', 'created_at'))
    return JsonResponse({'data': data})
    # return render(request, 'chart.html', {'data': data})

from django.shortcuts import render

def chart_view(request):
    return render(request, 'chart.html')


@csrf_exempt
def add_data(request):
    if request.method == 'POST':
        value = request.POST.get('value')
        DataPoint.objects.create(value=value)
        return JsonResponse({'status': 'success'})


from django.shortcuts import render, redirect
from .forms import SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # process the form data
            return redirect('success')
            
    else:
        form = SignUpForm()
    return render(request, 'signup2.html', {'form': form})

def success(request):
    return render(request, 'success.html')
