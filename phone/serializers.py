from django.contrib.auth import get_user_model
from rest_framework import serializers, exceptions, status
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _
from django.contrib.auth import authenticate
from django.contrib.auth import password_validation as validators


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

        if not user:
            raise exceptions.AuthenticationFailed(
                f"We didn't find a Notion account for this {username} address or phone number.",
                status.HTTP_401_UNAUTHORIZED,
            )
        return {
            "username": user.username,
            "phone_number": user.phone,
        }
