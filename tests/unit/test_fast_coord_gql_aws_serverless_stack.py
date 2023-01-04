import aws_cdk as core
import aws_cdk.assertions as assertions

from fast_coord_gql_aws_serverless.fast_coord_gql_aws_serverless_stack import FastCoordGqlAwsServerlessStack

# example tests. To run these tests, uncomment this file along with the example
# resource in fast_coord_gql_aws_serverless/fast_coord_gql_aws_serverless_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = FastCoordGqlAwsServerlessStack(app, "fast-coord-gql-aws-serverless")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
