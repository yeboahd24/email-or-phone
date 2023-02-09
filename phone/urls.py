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
    path("forms/", forms, name="forms"),
    path("game/<int:game_id>/", game_detail, name="game_detail"),
    path("game/<int:game_id>/move/", make_move, name="make_move"),
    path("games/", game_list, name="game_list"),
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset-confirm/<str:uidb64>/<str:token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path('get_data/', get_data, name='get_data'),
    path('chart/', chart_view, name='chart_view'),
    path('add_data/', add_data, name='add_data'),

    # path('players/int:player_id/', player_detail, name='player_detail'),
    # path('players/',player_list, name='player_list'),
]
