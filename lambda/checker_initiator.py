from constants import CHECKER_FN_NAME
import boto3
import json


# aws init
lambda_ = boto3.client("lambda")

n = 3


def CheckerInitiatorFn(event, context):
    # extract keyword from event
    bounds_list = event

    for i in range(0, len(bounds_list), n):
        lambda_.invoke(
            FunctionName=CHECKER_FN_NAME,
            InvocationType="Event",
            Payload=json.dumps(bounds_list[i : i + n]),
        )

    # return
    return
