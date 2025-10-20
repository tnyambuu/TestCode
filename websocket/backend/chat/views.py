# chat/views.py
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, mixins
from tasks.test_process import test_process

def index(request):
    return render(request, "chat/index.html")

def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})


class TestProcess(
    generics.GenericAPIView,
    mixins.ListModelMixin,
):

    def post(self, request):

        files = request.FILES.getlist('files')
        room_name = request.data.get('room_name')

        print('test process started')

        task_ids = []

        if not files:
            return Response({"error": "No files provided"}, status=400)

        for file in files:
            task_ids.append(test_process.delay(file_name=file.name, room_name=room_name).id)

        return Response({"task_ids": task_ids})
