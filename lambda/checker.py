from utilities.gql_utils import (
    get_total_data,
    get_header,
)
from utilities.queue_utils import send_batch, extract_message_bodies
from utilities.request_utils import make_http_request
from utilities.boundary_utils import create_child_boundary
from constants import KEYWORD

import boto3

import json
import math

ddb = boto3.resource("dynamodb")
quadTree = ddb.Table("QuadTree")

sqs = boto3.resource("sqs")
checkerQueue = sqs.get_queue_by_name(QueueName="CheckerQueue")
crawlerQueue = sqs.get_queue_by_name(QueueName="CrawlerQueue")
childNodeAdderQueue = sqs.get_queue_by_name(QueueName="ChildNodeAdderQueue")

lambda_ = boto3.client("lambda")


def CheckerFn(event, context):
    print(event)
    invoked = type(event) == list
    if invoked:
        bounds_list = event
    else:
        bounds_list = extract_message_bodies(event)
    print(bounds_list)

    # make request, repeat 3 times until success
    # if all failed, raise error
    header = get_header()
    data = get_total_data(bounds_list, KEYWORD)
    response = make_http_request(header, data)

    response_json = response.json()

    # get node from QuadTree
    ddb_response = ddb.batch_get_item(
        RequestItems={
            "QuadTree": {
                "Keys": [
                    {"bounds": bounds, "keyword": KEYWORD} for bounds in bounds_list
                ]
            }
        }
    )

    for i, bounds in enumerate(bounds_list):
        total_number = response_json[i]["data"]["businesses"]["total"]
        print(f"bounds-{bounds}, total_number-{total_number}")
        if total_number == 0:
            if invoked:
                print("total_number is zero, enqueueing")
                checkerQueue.send_message(
                    MessageBody=json.dumps(bounds, ensure_ascii=False)
                )
            else:
                print("total_number is zero, but it is from queue, ending")

            continue

        new_document = True
        for d in ddb_response["Responses"]["QuadTree"]:
            if d["bounds"] == bounds:
                document = d
                new_document = False
                print("Found existing document")
                print(document)
                break

        if new_document:
            print("Creating new document")

            document = {
                "bounds": bounds,
                "keyword": KEYWORD,
                "childs": [],
                "total_number": total_number,
            }
            quadTree.put_item(Item=document)

        elif total_number == d["total_number"]:
            print("total_number hasn't changed")
            continue

        else:
            print("Updating node on QuadTree")
            quadTree.update_item(
                Key={"bounds": bounds, "keyword": KEYWORD},
                UpdateExpression="SET total_number = :total_number",
                ExpressionAttributeValues={":total_number": total_number},
            )

            if total_number < d["total_number"]:
                print("total_number is less than current, ending")
                continue

        if total_number <= 300:
            print("total_number is less than 300, queueing to CrawlerQueue")
            message_amt = math.ceil(total_number / 50)
            messages = [
                {
                    "bounds": bounds,
                    "keyword": KEYWORD,
                    "start": i * 50 + 1,
                }
                for i in range(message_amt)
            ]

            send_batch(crawlerQueue, messages)
            continue

        if not document["childs"]:
            print("Creating node's childs")
            # create child
            childs = create_child_boundary(bounds)
            document["childs"] = childs

            # update childs on QuadTree
            quadTree.update_item(
                Key={"bounds": bounds, "keyword": KEYWORD},
                UpdateExpression="SET childs = :childs",
                ExpressionAttributeValues={":childs": document["childs"]},
            )

            # queue bounds, keyword to ChildNodeAdderQueue
            message = {
                "add_nodes": document["childs"],
                "delete_nodes": [bounds],
                "keyword": KEYWORD,
            }
            childNodeAdderQueue.send_message(
                MessageBody=json.dumps(message, ensure_ascii=False)
            )

        print("Invoking childs", document["childs"])
        send_batch(checkerQueue, document["childs"])
