from rest_framework import mixins
from .utils import *
from .models import Device
from django.utils import timezone


class DeviceMixin(mixins.CreateModelMixin):
    def create(self, request, *args, **kwargs):
        # Get the user's device information from the request
        ip_address = get_ip_address(request)
        device_name, device_details = get_device_details(
            request.META, str(refresh.access_token)
        )
        user = request.user
        device = Device.objects.create(
            user=user,
            last_request_datetime=timezone.now(),
            name=device_name,
            details=device_details,
            permanent_token=refresh,
            ip_address=ip_address,
        )
        device.save()
        user_device = Device.objects.filter(user=user).first()
        if (
            user_device.ip_address != ip_address
            or user_device.device.name != device_name
        ):
            warning_mail_send(user, ip_address)

        # Return the response for creating a new model instance
        return super().create(request, *args, **kwargs)
