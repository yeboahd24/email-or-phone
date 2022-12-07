from celery import shared_task
from datetime import timedelta
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from .models import Subscriber
from datetime import datetime
User = get_user_model()
@shared_task
def async_send_newsletter():
    '''
    Asynchronously send newsletter to all subscribers.
    Time period:
        - Time zone: Asia/Dhaka, Bangladesh.
        - Every weeks at 00:00 ⏰
    '''
    confirme_subscribers = Subscriber.objects.filter(confirmed=True)
    for subscriber in confirme_subscribers:
        body = render_to_string("newsletter.html")
        mail = EmailMessage(
            subject="Newsletter🎉",
            body=body,
            from_email=settings.EMAIL_HOST_USER,
            to=[subscriber.email],
        )
        mail.content_subtype = "HTML"
        mail.send()
        return "Newsletter sent to {}".format(subscriber.email)


@shared_task
def unlock_accounts():
    # Get the list of locked accounts
    locked_accounts = User.objects.filter(is_active=False)
    # Loop through the locked accounts and check if they have been locked for more than 5 minutes
    for account in locked_accounts:
        if (datetime.now().timestamp() - account.date_locked.timestamp()) >= 300:
            # If the account has been locked for more than 5 minutes, unlock it by setting the `is_active` flag to `True`
            account.is_active = True
            account.save()
