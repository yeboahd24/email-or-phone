from phone.views import *
from django.urls import path, re_path
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("notification/", notifications, name="notifications"),
    path("file/", FileUploadView.as_view()),
    re_path(r"stroke/(?P<filename>[^/]+)$", StrokeDataUpload.as_view()),
    # path("login/", auth_views.login, name="login"),
    # path("logout/", auth_views.logout, name="logout"),
    # path('recipes/<int:id>/', recipe, name='recipe'),
    # path('time', time, name='time'),
    path("time/", time_view, name="time"),
    path("reset/", reset_view, name="reset"),
    path("start/", start_view, name="start"),
    path("counter/", counter, name="counter"),
    path("stop/", stop, name="stop"),
    path(
        "subscriptions/", CreateSubscriptionView.as_view(), name="create-subscription"
    ),
    path("webhooks/payment/", PaymentWebhookView.as_view(), name="payment-webhook"),
    path("search/", search_movie, name="search_movie"),
]
