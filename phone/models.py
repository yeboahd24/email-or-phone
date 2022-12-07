from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)

import binascii
import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _
from django.core import validators
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import EmailPhoneUserManager
from .common_fields import BaseModel





class Device(models.Model):
    """
    Device model used for permanent token authentication
    """

    permanent_token = models.CharField(max_length=255, unique=True)
    jwt_secret = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
    name = models.CharField(_("Device name"), max_length=255)
    details = models.CharField(_("Device details"), max_length=255, blank=True)
    last_request_datetime = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # def save(self, *args, **kwargs):
    #     if not self.permanent_token:
    #         self.permanent_token = self.generate_key()

    #     return super(Device, self).save(*args, **kwargs)

    # def generate_key(self):
    #     return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.name


class AbstractEmailPhoneUser(AbstractBaseUser, PermissionsMixin):

    """Abstract User with the same behaviour as Django's default User."""

    username = models.CharField(
        _("email or phone"),
        max_length=255,
        unique=True,
        db_index=True,
        help_text=_(
            "Required. 255 characters or fewer. Letters, digits and " "@/./+/-/_ only."
        ),
        validators=[
            validators.RegexValidator(
                r"^[\w.@+-]+$",
                _(
                    "Enter a valid username. "
                    "This value may contain only letters, numbers "
                    "and @/./+/-/_ characters."
                ),
                "invalid",
            ),
        ],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_("email"), max_length=254, blank=True)
    phone = models.CharField(_("phone"), max_length=255, blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="device", null=True)
    date_locked = models.DateTimeField(null=True, blank=True)


    objects = EmailPhoneUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        abstract = True

    def get_full_name(self):
        """Return the full name for the user."""
        return self.username

    def get_short_name(self):
        """Return the short name for the user."""
        return self.username

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this User."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class EmailPhoneUser(AbstractEmailPhoneUser):

    """Concrete class of AbstractEmailPhoneUser.
    Use this if you don't need to extend EmailPhoneUser.
    """

    class Meta(AbstractEmailPhoneUser.Meta):
        swappable = "AUTH_USER_MODEL"




class Subscriber(BaseModel):
    email = models.EmailField(unique=True, verbose_name='Email')
    confirmed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'

    def __str__(self):
        return self.email + " (" + ("not " if not self.confirmed else "") + "confirmed)"
