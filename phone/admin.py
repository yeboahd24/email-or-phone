from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import EmailPhoneUser, Device, Stroke, MagicLink


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


class DeviceAdmin(admin.ModelAdmin):
    model = Device
    list_display = [
        "id",
        "user",
        "name",
        "created",
        "last_request_datetime",
    ]
    list_filter = [
        "id",
        "user",
        "name",
        "created",
        "last_request_datetime",
    ]
    search_fields = ["user__email", "name", "details"]
    fields = [
        "id",
        "name",
        "details",
        "created",
        "last_request_datetime",
        "permanent_token",
        "ip_address",
    ]
    readonly_fields = fields

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("user")

    def has_add_permission(self, request):
        return False


admin.site.register(Device, DeviceAdmin)
admin.site.register(Stroke)
admin.site.register(MagicLink)
