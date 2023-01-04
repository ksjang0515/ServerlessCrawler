import boto3
import json
from constants import (
    S3_BUCKET_NAME,
    S3_CHILDNODES_PATH,
    KEYWORD,
    CHECKER_INITIATOR_FN_NAME,
)

# aws init
s3 = boto3.resource("s3")
childNodes_obj = s3.Object(S3_BUCKET_NAME, f"{S3_CHILDNODES_PATH}/{KEYWORD}.json")
body = childNodes_obj.get()["Body"].read()
childNodes = json.loads(body)

lambda_ = boto3.client("lambda")
n = 99


def InitiatorFn(event, context):
    # for each keyword in keywords
    # queue keyword to InitiatorQueue
    for i in range(0, len(childNodes), n):
        lambda_.invoke(
            FunctionName=CHECKER_INITIATOR_FN_NAME,
            InvocationType="Event",
            Payload=json.dumps(childNodes[i : i + n], ensure_ascii=False),
        )

    # return
    return
