from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import EmailPhoneUser


class CustomUserAdmin(UserAdmin):
    model = EmailPhoneUser
    list_display = [
        "username",
        "email",
        "phone",
        "is_active",
        "date_joined",
    ]
    list_display_links = (
        "username",
        "email",
        "date_joined",
        "phone",
    )

    ordering = ("-date_joined",)



admin.site.register(EmailPhoneUser, CustomUserAdmin)
