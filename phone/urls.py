from phone.views import *
from django.urls import path, re_path


urlpatterns = [
    path("", notifications, name="notifications"),
    path("file/", FileUploadView.as_view()),
    re_path(r"stroke/(?P<filename>[^/]+)$", StrokeDataUpload.as_view()),
]
