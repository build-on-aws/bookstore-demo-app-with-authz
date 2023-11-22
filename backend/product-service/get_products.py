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

    # Handle authorization decision.
    product_list = handle_is_authorized(user_info)

    logger.info(f"Successfully returning product list - Count: {len(product_list)}")

    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps({"products": product_list}),
    }


def handle_is_authorized(user_info):
    # Construct the authorization request.
    authz_request = construct_authz_request(user_info)
    logger.info(f"Authorization request: {authz_request}")

    # Make the `is_authorized` call to Amazon Verified Permissions.
    response = verified_permissions_client.is_authorized(**authz_request)
    logger.info(f"Authorization response: {response}")

    # Determine which product list to return.
    return determine_product_list(response, user_info)


def construct_authz_request(user_info):
    entities = [
        {
            "identifier": {
                "entityType": "Bookstore::User",
                "entityId": user_info["username"]
            },
            "attributes": {},
            "parents": [
                {
                    "entityType": "Bookstore::Role",
                    "entityId": user_info["role"]
                }
            ]
        }
    ]

    resource = {
        "entityType": "Bookstore::Book",
        "entityId": "*"
    }

    action_id = "View"

    return {
        "policyStoreId": os.environ.get("POLICY_STORE_ID"),
        "principal": {
            "entityType": "Bookstore::User",
            "entityId": user_info["username"]
        },
        "action": {
            "actionType": "Bookstore::Action",
            "actionId": action_id
        },
        "resource": resource,
        "entities": {"entityList": entities},
        "context": {"contextMap": {}}
    }


def determine_product_list(response, user_info):
    if "decision" in response:
        if response["decision"] == "ALLOW":
            return books["books"]
        elif response["decision"] == "DENY":
            return []  # Return an empty list for denied access.

    return []
