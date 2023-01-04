from utilities.gql_utils import (
    get_items_data,
    get_header,
)
from utilities.request_utils import make_http_request
from utilities.queue_utils import extract_message_bodies

import boto3
import botocore

from datetime import datetime
import pytz


ddb = boto3.resource("dynamodb")
knownPlaces = ddb.Table("KnownPlaces")


def CrawlerFn(event, context):
    print(event)

    # extract bounds, keyword, start from event
    message_bodies = extract_message_bodies(event)
    message_body = message_bodies[0]

    bounds = message_body["bounds"]
    keyword = message_body["keyword"]
    start = message_body["start"]

    # make request, repeat 3 times until success
    # if all failed, raise error
    data = get_items_data(keyword, bounds, start, 50)
    header = get_header()
    response = make_http_request(header, data)

    detected_time = datetime.now(pytz.timezone("ASIA/SEOUL")).strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )

    # extract places from response
    response_json = response.json()
    items = response_json[0]["data"]["businesses"]["items"]

    # save places to KnownPlaces
    for item in items:
        address = item["roadAddress"] if item["roadAddress"] else item["fullAddress"]

        del item["roadAddress"]
        del item["fullAddress"]

        item["detected_time"] = detected_time
        item["address"] = address
        item["memo"] = ""

        try:
            knownPlaces.put_item(
                Item=item, ConditionExpression="attribute_not_exists(id)"
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
                raise

    # return
    return
