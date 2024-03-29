"""django_phone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from phone.views import *
from phone.handlers import grpc_handlers as user_grpc_handlers
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
from django_phone.settings import MEDIA_ROOT, MEDIA_URL

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("users/", UsersListView.as_view(), name="users"),
    path("login_2/", LoginView.as_view(), name="login_deff"),
    path("login/", LoginView.as_view(), name="login"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api-auth/", include("rest_framework.urls")),
    path("subscribe/", subscribe, name="subscribe"),
    path("unsubscribe/", unsubscribe, name="unsubscribe"),
    path("define/", get_definition, name="get_definition"),
    # path("not/", notifications, name="notifications"),
    path("", include("phone.urls")),
    path("stopwatch/", stopwatch, name="stopwatch"),
    # path("", include("django_private_chat2.urls", namespace="django_private_chat2")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path(
        "", include("django_private_chat2.urls", namespace="django_private_chat2")
    ),  # parler
)


def grpc_handlers(server):
    user_grpc_handlers(server)
