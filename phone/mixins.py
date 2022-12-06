from rest_framework import mixins, status
from .utils import *
from .models import Device
from django.utils import timezone
from rest_framework.response import Response


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


class LoginThrottlingMixin(mixins.CreateModelMixin):
    login_attempts_allowed = 3
    login_attempt_timeout = 5 # minutes
    print("mixins.LoginThrottlingMixin")
    def create(self, request, *args, **kwargs):
        print("locked testing")
        if request.user.is_authenticated:
            # Do not throttle authenticated users
            return super().create(request, *args, **kwargs)

        login_attempts = request.session.get('login_attempts', 0)
        last_login_attempt = request.session.get('last_login_attempt')

        if last_login_attempt and (timezone.now() - last_login_attempt).total_seconds() / 60 < self.login_attempt_timeout:
            # User has already made a login attempt within the timeout period
            login_attempts += 1
        else:
            # User has not made a login attempt or the timeout has expired
            login_attempts = 1
            request.user.is_active = True
            request.user.save()

        request.session['login_attempts'] = login_attempts
        request.session['last_login_attempt'] = timezone.now()

        if login_attempts > self.login_attempts_allowed:
            # Lock the user's account
            request.user.is_active = False
            request.user.save()
            print("locked")
            return Response({'error': 'Your account is locked. Please try again in {} minutes.'.format(self.login_attempt_timeout)},
                            status=status.HTTP_401_UNAUTHORIZED)

        return super().create(request, *args, **kwargs)
