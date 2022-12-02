import jwt

# from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import NotFound

# from devices.app_settings import api_settings as rfj_settings

from .models import Device
from rest_framework_simplejwt.settings import api_settings

# jwt_payload_handler = rfj_settings.JWT_DEVICES_PAYLOAD_HANDLER,

# jwt_response_payload_handler = rfj_settings.JWT_RESPONSE_PAYLOAD_HANDLER


def jwt_devices_get_secret_key(payload=None):
    try:
        return Device.objects.get(pk=payload.get("device_id")).jwt_secret.hex
    except Device.DoesNotExist:
        raise NotFound(_("Permanent token has expired."))


def jwt_devices_payload_handler(user, device=None):
    # payload = jwt_payload_handler(user)
    if device:
        payload["device_id"] = str(device.pk)
    return payload


def jwt_devices_encode_handler(payload):
    return jwt.encode(
        payload, jwt_devices_get_secret_key(payload), api_settings.JWT_ALGORITHM
    ).decode("utf-8")


def jwt_devices_response_payload_handler(token, user=None, request=None, **kwargs):
    """
    Returns the response data for both the login and refresh views.
    """
    data = jwt_devices_response_payload_handler(token, user, request)
    permanent_token = kwargs.get("permanent_token")
    if permanent_token:
        data["permanent_token"] = permanent_token
    device_id = kwargs.get("device_id")
    if device_id:
        data["device_id"] = device_id

    return data


def jwt_devices_decode_handler(token):
    options = {
        "verify_exp": api_settings.ACCESS_TOKEN_LIFETIME,
    }
    # get user from token, BEFORE verification, to get user secret key
    unverified_payload = jwt.decode(token, None, False)
    return jwt.decode(
        token,
        jwt_devices_get_secret_key(unverified_payload),
        api_settings.VERIFYING_KEY,
        options=options,
        leeway=api_settings.LEEWAY,
        audience=api_settings.AUDIENCE,
        issuer=api_settings.ISSUER,
        algorithms=[api_settings.ALGORITHM],
    )


def get_device_details(headers, token):
    device_name = headers.get("HTTP_X_DEVICE_MODEL")
    user_agent = headers.get("HTTP_USER_AGENT", "")
    if not device_name:
        device_name = user_agent
        device_details = ""
    else:
        device_details = user_agent

    return device_name, device_details
