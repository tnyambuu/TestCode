import time
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


# def ws_send(room, message):
#     print(f"Sending message: {message} to room: {room}")
#     layer = get_channel_layer()
#     layer.group_send(f"{room}", {"type": "task.update", "message": message})

def dump_process(room_name, task_id):

    layer = get_channel_layer()

    for count in range(10):
        async_to_sync(layer.group_send)(f"{room_name}", {"type": "task.update", "message": f"Processing {count + 1} / 10 in room {room_name} for task {task_id}"})
        time.sleep(1)