from utilities.queue_utils import extract_message_bodies
from constants import S3_BUCKET_NAME, S3_CHILDNODES_PATH

import boto3
import json

# aws init
s3 = boto3.resource("s3")


def ChildNodeAdderFn(event, context):
    print(event)

    # extract add_nodes and delete_nodes from event
    message_bodies = extract_message_bodies(event)
    message_body = message_bodies[0]

    keyword = message_body["keyword"]
    add_nodes = message_body["add_nodes"]
    delete_nodes = message_body["delete_nodes"]

    # get ChildNodes
    childNodes_obj = s3.Object(S3_BUCKET_NAME, f"{S3_CHILDNODES_PATH}/{keyword}.json")
    body = childNodes_obj.get()["Body"].read()
    childNodes = json.loads(body)

    # delete delete_nodes
    for delete_node in delete_nodes:
        if delete_node in childNodes:
            childNodes.remove(delete_node)

    # add add_nodes
    for add_node in add_nodes:
        if add_node not in childNodes:
            childNodes.append(add_node)

    # save ChildNodes
    childNodes_obj.put(
        Body=bytes(json.dumps(childNodes, ensure_ascii=False), encoding="utf-8")
    )

    # return
    return
