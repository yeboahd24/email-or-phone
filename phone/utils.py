from django.core.mail import send_mail
from django.conf import settings

def get_device_details(headers, token):
    device_name = headers.get("HTTP_X_DEVICE_MODEL")
    user_agent = headers.get("HTTP_USER_AGENT", "")
    if not device_name:
        device_name = user_agent
        device_details = ""
    else:
        device_details = user_agent

    return device_name, device_details




def get_ip_address(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip



def warning_mail_send(user_email, ip_address):
    text_content = f"we recorded an attempt to log in to your account with this ip address {ip_address}. If it was you, then simply" \
                   'ignore this letter. If it wasn’t you - contact the site administration as soon as possible.'
    subject = 'Attempt to log in to your account'
    from_email = settings.DEFAULT_FROM_EMAIL
    # receive warning mail
    mail_sent = send_mail(subject, text_content, from_email, [user_email])

    return mail_sent


