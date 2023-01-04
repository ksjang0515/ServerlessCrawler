import json
from uuid import uuid4


def extract_message_bodies(event):
    message_bodies = [json.loads(r["body"]) for r in event["Records"]]

    return message_bodies


def send_batch(queue, messages):
    items = [0 for _ in range(10)]
    cnt = 0

    for message in messages:
        items[cnt] = {
            "MessageBody": json.dumps(message, ensure_ascii=False),
            "Id": str(uuid4()),
        }
        # print(items[cnt])

        cnt += 1
        if cnt >= 10:
            # print("Enqueueing Items")
            queue.send_messages(Entries=items)
            cnt = 0

    if cnt != 0:
        # print("Enqueueing Items")
        queue.send_messages(Entries=items[:cnt])
