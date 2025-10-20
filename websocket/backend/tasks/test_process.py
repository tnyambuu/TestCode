import logging
from celery import group, shared_task
from django.core.cache import cache
import time
import os
import multiprocessing
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import asyncio
from util.utils import dump_process


def run_coro(coro):
    try:
        loop = asyncio.get_running_loop()   # already running in this thread?
    except RuntimeError:
        asyncio.run(coro)                   # no loop → run blocking
    else:
        loop.create_task(coro)              # loop exists → schedule

async def _ws_send(room, data):
    layer = get_channel_layer()
    await layer.group_send(f"chat_{room}", {"type": "task.update", "data": data})


@shared_task(bind=True)
def test_process(self, file_name, room_name):

    task_id = getattr(self.request, "id", None)
    pid = os.getpid()                      # OS process ID
    proc = multiprocessing.current_process().name

    # run_coro(_ws_send(room_name, {"task_id": task_id, "message": "Started", "progress": 0}))

    logging.info(f"Starting task {task_id} for file {file_name}")
    logging.info(f"task_id={task_id} pid={pid} process={proc} file={file_name} room={room_name}")

    dump_process(room_name, task_id)

    # for i in range(10):
    #     logging.info(f"Processing file {file_name} in room {room_name} - {i+1}/10")

    #     run_coro(_ws_send(room_name, {"task_id": task_id, "message": "Started", "progress": f"Processing file {file_name} in room {room_name} - {i+1}/10"}))
    #     time.sleep(1)

    # run_coro(_ws_send(room_name, {"task_id": task_id, "message": "Started", "progress": 0}))

    logging.info(f"Task {task_id} completed")
    return {"task_id": task_id, "pid": pid, "process": proc}