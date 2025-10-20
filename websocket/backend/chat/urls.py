# chat/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("client/<str:room_name>/", views.room, name="room"),
    path("server/test-process/", views.TestProcess.as_view(), name="test_process"),
]