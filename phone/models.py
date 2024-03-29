from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)

import binascii
import os
import uuid
from django.core.validators import MaxValueValidator, MinValueValidator

from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _
from django.core import validators
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import EmailPhoneUserManager
from .common_fields import BaseModel

# from django.contrib.auth import get_user_model

# User = get_user_model()


class Device(models.Model):
    """
    Device model used for permanent token authentication
    """

    permanent_token = models.CharField(max_length=255, unique=True)
    jwt_secret = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user"
    )
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
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="device", null=True
    )
    date_locked = models.DateTimeField(null=True, blank=True)
    otp = models.CharField(max_length=255, null=True, blank=True)

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
    email = models.EmailField(unique=True, verbose_name="Email")
    confirmed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Subscriber"
        verbose_name_plural = "Subscribers"

    def __str__(self):
        return self.email + " (" + ("not " if not self.confirmed else "") + "confirmed)"


class Notification(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


from django.contrib.auth import get_user_model

User = get_user_model()


class Stroke(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="stroke")
    glucose_level = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(5), MaxValueValidator(150)],
        blank=True,
        null=True,
        verbose_name=_("Glucose level"),
    )
    bmi = models.FloatField(
        null=True,
        blank=True,
        default=None,
        verbose_name=_("BMI"),
        help_text=None,
    )
    blood_pressure_systolic = models.PositiveIntegerField(
        validators=[MinValueValidator(70), MaxValueValidator(300)],
        blank=True,
        null=True,
        verbose_name=_("Blood pressure systolic"),
    )
    blood_pressure_diastolic = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(10), MaxValueValidator(150)],
        blank=True,
        null=True,
        verbose_name=_("Blood pressure diastolic"),
    )
    age = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(13), MaxValueValidator(110)],
        blank=True,
        null=True,
        verbose_name=_("Age"),
    )

    def __str__(self):
        return "Stroke({}) for user: {}".format(self.id, self.user)

 


from datetime import datetime
from dateutil import rrule


class Subscription(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    frequency = models.CharField(
        max_length=10, choices=[("monthly", "Monthly"), ("yearly", "Yearly")]
    )
    next_delivery_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # user = models.ForeignKey(
    #     EmailPhoneUser, on_delete=models.CASCADE, related_name="subscriptions"
    # )

    def __str__(self):
        return f"Subscription {self.id}"

    def delivery_dates(self):
        if self.frequency == "monthly":
            return list(
                rrule.rrule(rrule.MONTHLY, dtstart=self.start_date, until=self.end_date)
            )
        elif self.frequency == "yearly":
            return list(
                rrule.rrule(rrule.YEARLY, dtstart=self.start_date, until=self.end_date)
            )

    def set_next_delivery_date(self):
        if self.frequency == "monthly":
            self.next_delivery_date = rrule.rrule(
                rrule.MONTHLY, dtstart=self.start_date, until=self.end_date
            ).after(datetime.now())
        elif self.frequency == "yearly":
            self.next_delivery_date = rrule.rrule(
                rrule.YEARLY, dtstart=self.start_date, until=self.end_date
            ).after(datetime.now())


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Subscription)
def set_next_delivery(sender, instance, **kwargs):
    instance.set_next_delivery_date()


class MagicLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.CharField(max_length=255)
    expires_at = models.DateTimeField(auto_now_add=True)


class Player(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=1)
    games_played = models.PositiveIntegerField(default=0)
    games_won = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Game(models.Model):
    board = models.CharField(max_length=9, default="-" * 9)
    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Game {self.id}"

    def next_player(self):
        x_count = self.board.count("X")
        o_count = self.board.count("O")
        if x_count <= o_count:
            return Player.objects.get(symbol="X")
        else:
            return Player.objects.get(symbol="O")

    def is_finished(self):
        board = self.board
        if board[0] == board[1] == board[2] and board[0] != " ":
            return True
        elif board[3] == board[4] == board[5] and board[3] != " ":
            return True
        elif board[6] == board[7] == board[8] and board[6] != " ":
            return True
        elif board[0] == board[3] == board[6] and board[0] != " ":
            return True
        elif board[1] == board[4] == board[7] and board[1] != " ":
            return True
        elif board[2] == board[5] == board[8] and board[2] != " ":
            return True
        elif board[0] == board[4] == board[8] and board[0] != " ":
            return True
        elif board[2] == board[4] == board[6] and board[2] != " ":
            return True
        else:
            return False


from django.contrib.auth.models import User
from django.db import models


class PasswordResetToken(models.Model):
    token = models.CharField(max_length=100, unique=True)
    user = models.OneToOneField(EmailPhoneUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


class DataPoint(models.Model):
    value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DataPoint {self.value}"


# models.py


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    like_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class FormStep1(models.Model):
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()


class FormStep2(models.Model):
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=200, blank=True)

class MyModel(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name



from parler.models import TranslatableModel, TranslatedFields

class Book(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=200, blank=True, null=True),
        author=models.CharField(max_length=100, blank=True, null=True),
        description=models.TextField(blank=True, null=True),
    )

    def __str__(self):
        return self.title



class Image(models.Model):
    image = models.ImageField(upload_to='images/')


class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    unread = models.BooleanField(default=True)





class Signup(models.Model):
    # fields for signup model
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=50)

    class Meta:
        db_table = 'signup'
        app_label = 'blog'
        managed = True

class Posts(models.Model):
    # fields for posts model
    title = models.CharField(max_length=100)
    content = models.TextField()

    class Meta:
        db_table = 'posts'
        app_label = 'blog'
        managed = True
