import boto3
import json
import os
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from shared import get_user_claims

logger = Logger()
tracer = Tracer()

with open("database.json", "r") as database:
    books = json.load(database)

HEADERS = {
    "Access-Control-Allow-Origin": os.environ.get("ALLOWED_ORIGIN"),
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,GET",
    "Access-Control-Allow-Credentials": True,
}

verified_permissions_client = boto3.client("verifiedpermissions")


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: LambdaContext):
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")

    # Obtain user information.
    source_ip = event.get("requestContext", {}).get("identity", {}).get("sourceIp")
    jwt_token = event["headers"].get("Authorization")
    user_info = {"username": "Unknown", "role": "Unknown", "yearsAsMember": "Unknown", "region": "Unknown"}

    if jwt_token:
        user_info = get_user_claims(jwt_token, source_ip)

    logger.info(f"User info: {user_info}")

    # No authorization.
    product_list = books["books"]

    logger.info(f"Successfully returning product list - Count: {len(product_list)}")

    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps({"products": product_list}),
    }
