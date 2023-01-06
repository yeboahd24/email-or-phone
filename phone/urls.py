from phone.views import *
from django.urls import path, re_path
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", notifications, name="notifications"),
    path("file/", FileUploadView.as_view()),
    re_path(r"stroke/(?P<filename>[^/]+)$", StrokeDataUpload.as_view()),
    path("login/", auth_views.login, name="login"),
    path("logout/", auth_views.logout, name="logout"),
    path('recipes/<int:id>/', recipe, name='recipe'),

]
