from constants import (
    TIMESTREAM_DB_NAME,
    TIMESTREAM_TABLE_NAME,
    TIMESTREAM_REGION,
)

import boto3

ts = boto3.client("timestream-write", region_name=TIMESTREAM_REGION)

# {"eventName":["INSERT"]}
def ListenerFn(event, context):
    print(event)
    try:
        ts.write_records(
            DatabaseName=TIMESTREAM_DB_NAME,
            TableName=TIMESTREAM_TABLE_NAME,
            Records=[
                {
                    "Dimensions": [{"Name": "Site", "Value": "N"}],
                    "MeasureName": "NewPlace",
                    "MeasureValue": record["dynamodb"]["Keys"]["id"]["S"],
                    "MeasureValueType": "DOUBLE",
                    "Time": str(int(record["dynamodb"]["ApproximateCreationDateTime"])),
                    "TimeUnit": "SECONDS",
                }
                for record in event["Records"]
            ],
        )
    except Exception as e:
        print(e)
