from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as lambda_,
    aws_lambda_python_alpha as lambda_python_,
    aws_dynamodb as dynamodb_,
    aws_sqs as sqs_,
    aws_lambda_event_sources as event_source_,
    aws_events as events_,
    aws_events_targets as targets_,
    aws_s3 as s3_,
    aws_iam as iam_,
)
from constructs import Construct


class FastCoordGqlAwsServerlessStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # DynamoDB - Address Table
        quadTree = dynamodb_.Table(
            self,
            "QuadTree",
            table_name="QuadTree",
            partition_key=dynamodb_.Attribute(
                name="bounds", type=dynamodb_.AttributeType.STRING
            ),
            sort_key=dynamodb_.Attribute(
                name="keyword", type=dynamodb_.AttributeType.STRING
            ),
            billing_mode=dynamodb_.BillingMode.PAY_PER_REQUEST,
        )

        # DynamoDB - Places Table
        knownPlaces = dynamodb_.Table(
            self,
            "KnownPlaces",
            table_name="KnownPlaces",
            partition_key=dynamodb_.Attribute(
                name="id", type=dynamodb_.AttributeType.STRING
            ),
            billing_mode=dynamodb_.BillingMode.PAY_PER_REQUEST,
            stream=dynamodb_.StreamViewType.NEW_IMAGE,
        )

        # S3
        s3 = s3_.Bucket(self, "keywords", bucket_name="fast-coord-gql-crawler")

        # SQS
        checkerQueue = sqs_.Queue(self, "CheckerQueue", queue_name="CheckerQueue")
        crawlerQueue = sqs_.Queue(self, "CrawlerQueue", queue_name="CrawlerQueue")
        childNodeAdderQueue = sqs_.Queue(
            self, "ChildNodeAdderQueue", queue_name="ChildNodeAdderQueue"
        )

        # Initiator
        initiatorFn = lambda_python_.PythonFunction(
            self,
            "InitiatorFn",
            function_name="InitiatorFn",
            entry="./lambda",
            index="initiator.py",
            handler="InitiatorFn",
            runtime=lambda_.Runtime.PYTHON_3_9,
            timeout=Duration.seconds(5),
            reserved_concurrent_executions=1,
        )

        # CheckerInitiator
        checkerInitiatorFn = lambda_python_.PythonFunction(
            self,
            "CheckerInitiatorFn",
            function_name="CheckerInitiatorFn",
            entry="./lambda",
            index="checker_initiator.py",
            handler="CheckerInitiatorFn",
            runtime=lambda_.Runtime.PYTHON_3_9,
            timeout=Duration.seconds(5),
            reserved_concurrent_executions=20,
        )

        # Checker
        checkerFn = lambda_python_.PythonFunction(
            self,
            "CheckerFn",
            function_name="CheckerFn",
            entry="./lambda",
            index="checker.py",
            handler="CheckerFn",
            runtime=lambda_.Runtime.PYTHON_3_9,
            timeout=Duration.seconds(20),
            reserved_concurrent_executions=400,
        )

        # Crawler
        crawlerFn = lambda_python_.PythonFunction(
            self,
            "CrawlerFn",
            function_name="CrawlerFn",
            entry="./lambda",
            index="crawler.py",
            handler="CrawlerFn",
            runtime=lambda_.Runtime.PYTHON_3_9,
            timeout=Duration.seconds(20),
            reserved_concurrent_executions=200,
        )

        # Listener
        listenerFn = lambda_python_.PythonFunction(
            self,
            "ListenerFn",
            function_name="ListenerFn",
            entry="./lambda",
            index="listener.py",
            handler="ListenerFn",
            runtime=lambda_.Runtime.PYTHON_3_9,
            reserved_concurrent_executions=10,
            retry_attempts=0,
        )
        listenerFn.add_to_role_policy(
            iam_.PolicyStatement(
                effect=iam_.Effect.ALLOW,
                actions=["timestream:WriteRecords"],
                resources=[
                    "arn:aws:timestream:ap-northeast-1:416143312127:database/TimestreamTest/table/TestTable"
                ],
            )
        )
        listenerFn.add_to_role_policy(
            iam_.PolicyStatement(
                effect=iam_.Effect.ALLOW,
                actions=["timestream:DescribeEndpoints"],
                resources=["*"],
            )
        )

        # ChildNodeAdderFn
        childNodeAdderFn = lambda_python_.PythonFunction(
            self,
            "ChildNodeAdderFn",
            function_name="ChildNodeAdderFn",
            entry="./lambda",
            index="adder.py",
            handler="ChildNodeAdderFn",
            runtime=lambda_.Runtime.PYTHON_3_9,
            timeout=Duration.seconds(10),
            reserved_concurrent_executions=1,
        )

        # DynamoDB Permission
        quadTree.grant_read_write_data(checkerFn)

        knownPlaces.grant_write_data(crawlerFn)
        # knownPlaces.grant_read_data(listenerFn)

        # Lambda Permission
        checkerInitiatorFn.grant_invoke(initiatorFn)
        checkerFn.grant_invoke(checkerInitiatorFn)

        # SQS Permission
        checkerQueue.grant_send_messages(checkerFn)
        checkerQueue.grant_consume_messages(checkerFn)

        crawlerQueue.grant_send_messages(checkerFn)
        crawlerQueue.grant_consume_messages(crawlerFn)

        childNodeAdderQueue.grant_send_messages(checkerFn)
        childNodeAdderQueue.grant_consume_messages(childNodeAdderFn)

        # Event Listener
        # CheckerQueue trigger CheckerFn
        event_source = event_source_.SqsEventSource(checkerQueue, batch_size=3)
        checkerFn.add_event_source(event_source)

        # CrawlerQueue trigger CrawlerFn
        event_source = event_source_.SqsEventSource(crawlerQueue, batch_size=1)
        crawlerFn.add_event_source(event_source)

        # ChildNodeAdderQueue trigger ChildNodeAdderFn
        event_source = event_source_.SqsEventSource(childNodeAdderQueue, batch_size=1)
        childNodeAdderFn.add_event_source(event_source)

        # KnownPlaces trigger ListenerFn
        event_source = event_source_.DynamoEventSource(
            knownPlaces,
            starting_position=lambda_.StartingPosition.LATEST,
            # filters=[{"eventName": [lambda_.FilterRule.is_equal("INSERT")]}],
        )
        listenerFn.add_event_source(event_source)

        # S3 Permission
        s3.grant_read(initiatorFn)
        s3.grant_read_write(childNodeAdderFn)
