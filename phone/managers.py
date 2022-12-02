from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class EmailPhoneUserManager(BaseUserManager):

    """Custom Manager for EmailPhoneUser.
    For Examples check Django code:
    https://github.com/django/django/blob/master/django/contrib/auth/models.py
    """

    def normalize_phone(self, phone, country_code=None):
        phone = phone.strip().lower()
        try:
            import phonenumbers

            phone_number = phonenumbers.parse(phone, country_code)
            phone = phonenumbers.format_number(
                phone_number, phonenumbers.PhoneNumberFormat.E164
            )
        except ImportError:
            pass

        return phone

    def _create_user(
        self, email_or_phone, password, is_staff, is_superuser, **extra_fields
    ):
        """Create EmailPhoneUser with the given email or phone and password.
        :param str email_or_phone: user email or phone
        :param str password: user password
        :param bool is_staff: whether user staff or not
        :param bool is_superuser: whether user admin or not
        :return settings.AUTH_USER_MODEL user: user
        :raise ValueError: email or phone is not set
        :raise NumberParseException: phone does not have correct format
        """
        if not email_or_phone:
            raise ValueError("The given email_or_phone must be set")

        if "@" in email_or_phone:
            email_or_phone = self.normalize_email(email_or_phone)
            username, email, phone = (email_or_phone, email_or_phone, "")
        else:
            phone = self.normalize_phone(
                email_or_phone, country_code=extra_fields.get("country_code")
            )
            username, email, phone = (email_or_phone, "", email_or_phone)

        now = timezone.now()
        is_active = extra_fields.pop("is_active", True)
        user = self.model(
            username=username,
            email=email,
            phone=phone,
            is_staff=is_staff,
            is_active=is_active,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email_or_phone, password=None, **extra_fields):
        return self._create_user(email_or_phone, password, False, False, **extra_fields)

    def _create_superuser(
        self, username, password, is_staff, is_superuser, **extra_fields
    ):
        user = self.model(
            username=username,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=timezone.now(),
            date_joined=timezone.now(),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        return self._create_superuser(
            username, password, is_staff=True, is_superuser=True, **extra_fields
        )
