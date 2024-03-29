from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    EmailPhoneUser,
    Device,
    Stroke,
    MagicLink,
    Game,
    Player,
    DataPoint,
    Post,
    FormStep1,
    FormStep2,
    MyModel,
    Book
)


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




from parler.admin import TranslatableAdmin

class BookAdmin(TranslatableAdmin):
    fields = ('title', 'author', 'description')

admin.site.register(Book, BookAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Stroke)
admin.site.register(MagicLink)
admin.site.register(Game)
admin.site.register(Player)
admin.site.register(DataPoint)
admin.site.register(Post)
admin.site.register(FormStep1)
admin.site.register(FormStep2)
admin.site.register(MyModel)



