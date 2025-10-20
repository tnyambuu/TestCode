import time
from channels.layers import get_channel_layer


async def ws_send(room, data):
    layer = get_channel_layer()
    await layer.group_send(f"chat_{room}", {"type": "task.update", "data": data})

def dump_process(room_name, task_id):

    for count in range(10):
        print(f"Processing {count} in room {room_name} for task {task_id}")
        ws_send(room_name, {"task_id": task_id, "message": "Started", "progress": count})
        time.sleep(1)