from phone.views import *
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.views.i18n import set_language


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
    path("get_data/", get_data, name="get_data"),
    path("chart/", chart_view, name="chart_view"),
    path("add_data/", add_data, name="add_data"),
    path("signup/", signup, name="signup"),
    path("success/", success, name="success"),
    path("code/", code_upload, name="code_upload"),
    path("like_post/<int:post_id>/", like_post_view, name="like_post"),
    path("post_list/", post_list, name="post_list"),
    path("list/", list, name="list"),
    path("form_step1/", form_step1, name="form_step1"),
    path("form_step2/", form_step2, name="form_step2"),
    path("my_view/", my_view, name="my_view"),
    path("get_choices/", get_choices, name="search"),
    path("contact/", contact, name="contact"),
    path("remember/", CustomLoginView.as_view(), name="remember"),
    path("callback/", supabase_callback, name="callback"),
    path("login/", login, name="login"),
    path("books/", book_list, name="books"),
    path('set-language/', set_language, name='set_language'),
    path('password_strength/', password_strength, name='password_strength'),
    path("validate_password_strength/", validate_password_strength, name="validate_password_strength"),

    # path("signin/", LoginView.as_view(), name="signin"),
    # path("test/", login_supabase, name="test"),
    # path('players/int:player_id/', player_detail, name='player_detail'),
    # path('players/',player_list, name='player_list'),
]
# urls.py
