from django.contrib.auth import get_user_model
from rest_framework import serializers, exceptions, status
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _
from django.contrib.auth import authenticate
from django.contrib.auth import password_validation as validators
from .models import Device, Subscription
from .utils import *
from django.utils import timezone
from django_grpc_framework import generics, proto_serializers
from user_proto import user_pb2

User = get_user_model()


class UsersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "username",
            "date_joined",
        ]


# Register user with either email or phone
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "password",
        ]

    def validate(self, data):
        if not data.get("password"):
            raise serializers.ValidationError("Please enter a password and")

        user = User(**data)
        password = data.get("password")
        errors = dict()
        try:
            validators.validate_password(password=password, user=user)
        except exceptions.ValidationError as e:
            errors["password"] = list(e.messages)
        if errors:
            raise serializers.ValidationError(errors)
        return super(UserRegisterSerializer, self).validate(data)

    def create(self, validated_data):
        username = validated_data["username"]
        password = validated_data["password"]
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {"detail": "phone number or email addresses must be unique."}
            )
        user = User.objects.create_user(email_or_phone=username)
        user.set_password(password)
        user.save()
        return user
        # return super().create(validated_data)


# Login Serializer
class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=255, min_length=3, help_text="Email or Phone", label="Email or Phone"
    )
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        username = attrs.get("username", "")
        password = attrs.get("password", "")

        user = authenticate(username=username, password=password)
        user_test = User.objects.get(username=username)
        print("is_active", user_test.is_active)

        # token = self.context["access"].META
        # device_name, device_details = get_device_details(
        #     self.context["request"].META, token
        # )
        # print("token", token)
        # device = Device.objects.create(
        #     user=user,
        #     last_request_datetime=timezone.now(),
        #     name=device_name,
        #     details=device_details,
        #     permanent_token=token,
        # )
        # device.save()

        if not user:
            raise exceptions.AuthenticationFailed(
                f"We didn't find a Notion account for this {username} account.",
                status.HTTP_401_UNAUTHORIZED,
            )
        return {
            "username": user.username,
            "phone_number": user.phone,
        }


class UserProtoSerializer(proto_serializers.ModelProtoSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        proto_class = user_pb2.User
        fields = [
            "username",
            "password",
        ]

    def validate(self, data):
        if not data.get("password"):
            raise serializers.ValidationError("Please enter a password and")

        user = User(**data)
        password = data.get("password")
        errors = dict()
        try:
            validators.validate_password(password=password, user=user)
        except exceptions.ValidationError as e:
            errors["password"] = list(e.messages)
        if errors:
            raise serializers.ValidationError(errors)
        return super().validate(data)

    def create(self, validated_data):
        username = validated_data["username"]
        password = validated_data["password"]
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {"detail": "phone number or email addresses must be unique."}
            )
        user = User.objects.create_user(email_or_phone=username)
        user.set_password(password)
        user.save()
        return user
        # return supe


# from django.contrib.auth.hashers import make_password

# class UserProtoSerializer(proto_serializers.ModelProtoSerializer):


#     class Meta:
#         model = User
#         proto_class = user_pb2.User
#         fields = ['username', 'password']

#     def create(self, validated_data):
#         user = User.objects.create(
#             username=validated_data['username'],
#             password=make_password(validated_data['password'])
#         )
#         return user


class StrokeDataUploadSerializer(serializers.Serializer):
    stroke = serializers.FileField()

    class Meta:
        fields = ["stroke"]


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"


# New Flow


class UserSignUP(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "username",
        ]



class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()




class PasswordResetConfirmSerializer(serializers.Serializer):
    # password input field
    new_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    # make the new password field required
    def validate_new_password(self, value):
        if not value:
            raise serializers.ValidationError("This field is required.")
        return value


