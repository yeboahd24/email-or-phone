from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView, CreateAPIView
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login

from django.contrib.auth import get_user_model
from .serializers import UserRegisterSerializer, UsersListSerializer, LoginSerializer
from .models import EmailPhoneUser, Device
from .utils import *
from django.utils import timezone
from django.contrib import messages
from .models import Subscriber
from django.db import IntegrityError
from .tasks import async_send_newsletter
from django.shortcuts import redirect


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




def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        subscriber = Subscriber(email=email, confirmed=True)
        if subscriber == Subscriber.objects.filter(email=subscriber.email):
            messages.error(request, 'You are already subscribed to our newsletter!')
            return redirect('login')
        else:
            try:
                subscriber.save()
                async_send_newsletter.delay()
                messages.success(request, 'You have been subscribed to our newsletter!')
                return redirect('login')
            except IntegrityError as e:
                messages.error(request, 'You are already subscribed to our newsletter!')
                return redirect('login')
    else:
        return redirect('login')


def unsubscribe(request):
    confirme_subscribers = Subscriber.objects.get(email=request.GET['email'])
    for subscriber in confirme_subscribers:
        subscriber.delete()
        messages.success(request, 'You have successfully unsubscribed from our newsletter!')
        return redirect('login')
