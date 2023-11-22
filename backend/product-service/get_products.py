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
    "Access-Control-Allow-Headers": "Content-Type,Authorization,authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Access-Control-Allow-Credentials": True,
}

POLICIES = {
    "PUBLISHERS_VIEW": "Allows publishers to list books they have published",
    "PUBLISHER_ACCESS_TO_ONE_BOOK": "Allows specific Publisher to list a specific book",
    "PREMIUM_OFFERS": "Allows customers with specific value for yearsAsMember attribute to list premium offers",
    "NO_PREMIUM_OFFERS": "Denies customers with specific value for yearsAsMember attribute to list premium offers",
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
    product_list = (
        handle_is_authorized(user_info) if user_info["role"] != "Publisher" else handle_batch_is_authorized(user_info)
    )

    logger.info(f"Successfully returning product list - Count: {len(product_list)}")

    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps({"products": product_list}),
    }


def get_policy_description(response):
    logger.info(f"Response information: {response}")
    policy_id = response.get("determiningPolicies", [{}])[0].get("policyId")

    if policy_id:
        policy_response = verified_permissions_client.get_policy(
            policyStoreId=os.environ.get("POLICY_STORE_ID"),
            policyId=policy_id
        )
        return policy_response.get("definition", {}).get("static", {}).get("description")

    return ""


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

    # Determine action ID based on user role and yearsAsMember.
    action_id = "View"

    if user_info["role"] == "Customer":
        years_as_member = user_info.get("yearsAsMember", 0)

        if years_as_member != "Unknown":
            action_id = "ViewWithPremiumOffers"
            entities[0]["attributes"]["yearsAsMember"] = {"long": int(years_as_member)}

    # Set `region` attribute in the context based on the specific user attributes.
    region = user_info.get("region", "Unknown")
    context_map = {"region": {"string": region}}

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
        "context": {"contextMap": context_map}
    }


def determine_product_list(response, user_info):
    if "decision" in response:
        if response["decision"] == "ALLOW":
            policy_description = get_policy_description(response)

            if user_info["role"] == "Publisher" and policy_description == POLICIES["PUBLISHERS_VIEW"]:
                # Return books published by this publisher.
                return [book for book in books["books"] if book["publisher"] == user_info["username"]]

            # If allowed and not a publisher, return all books including premium offers.
            return books["books"]
        elif response["decision"] == "DENY":
            # Handle the deny decision for customers.
            if user_info["role"] == "Customer":
                policy_description = get_policy_description(response)

                if policy_description == POLICIES["NO_PREMIUM_OFFERS"]:
                    # Return regular books for customers without premium offers.
                    return [book for book in books["books"] if not book["premiumOffer"]]

            return []  # Return an empty list for denied access.

    return []


def handle_batch_is_authorized(user_info):
    # Construct the batch authorization request.
    batch_authz_request = construct_batch_authz_request(user_info)
    logger.info(f"Batch authorization request: {batch_authz_request}")

    # Make `batch_is_authorized` call to Amazon Verified Permissions.
    responses = verified_permissions_client.batch_is_authorized(**batch_authz_request)
    logger.info(f"Batch authorization response: {responses}")

    return determine_product_list_for_publisher(responses, user_info)


def construct_batch_authz_request(user_info):
    evaluated_user = {
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

    # Always one action ID in this case.
    action_id = "View"

    # Set `region` attribute in the context based on the specific user attributes.
    region = user_info.get("region", "Unknown")
    context_map = {"region": {"string": region}}

    book_owned_by_william = "em1oadaa-b22k-4ea8-kk33-f6m217604o3m"
    book_owned_by_dante = "fn2padaa-c33l-4ea8-ll44-g7n217604p4n"

    batch_request = {
        "policyStoreId": os.environ.get("POLICY_STORE_ID"),
        "entities": {
            "entityList": [
                evaluated_user,

                # Here we add books that will be evaluated against publishers.
                # In our example, each of two Publishers - Dante and William - have just one book.
                # However, we have added new policy, that Dante can list a specific book owned by William.

                get_publisher_book_entity(book_owned_by_william, "William"),
                get_publisher_book_entity(book_owned_by_dante, "Dante")
            ]
        },
        "requests": [
            {
                "principal": {
                    "entityType": "Bookstore::User",
                    "entityId": user_info["username"]
                },
                "action": {
                    "actionType": "Bookstore::Action",
                    "actionId": action_id
                },
                "resource": {
                    "entityType": "Bookstore::Book",
                    "entityId": book_owned_by_william
                },
                "context": {
                    "contextMap": context_map
                }
            },
            {
                "principal": {
                    "entityType": "Bookstore::User",
                    "entityId": user_info["username"]
                },
                "action": {
                    "actionType": "Bookstore::Action",
                    "actionId": action_id
                },
                "resource": {
                    "entityType": "Bookstore::Book",
                    "entityId": book_owned_by_dante
                },
                "context": {
                    "contextMap": context_map
                }
            }
        ]
    }

    return batch_request


def get_publisher_book_entity(book_id, username):
    return {
        "identifier": {
            "entityType": "Bookstore::Book",
            "entityId": book_id
        },
        "attributes": {
            "owner": {
                "entityIdentifier": {
                    "entityType": "Bookstore::User",
                    "entityId": username
                }
            }
        },
        "parents": []
    }


def determine_product_list_for_publisher(responses, user_info):
    allowed_books = []

    for response in responses.get("results", []):
        if response.get("decision") == "ALLOW":
            policy_description = get_policy_description(response)

            # Check if the policy allows the publisher to list the books they have published.
            # If not, check the other policy, if that allows a specific user to list a specific book.
            if policy_description == POLICIES["PUBLISHERS_VIEW"]:
                allowed_books.extend([book for book in books["books"] if book["publisher"] == user_info["username"]])
            elif policy_description == POLICIES["PUBLISHER_ACCESS_TO_ONE_BOOK"]:
                book_id = response["request"]["resource"]["entityId"]
                allowed_books.extend([book for book in books["books"] if book["id"] == book_id])

    # Remove duplicates, if any.
    allowed_books = [dict(t) for t in {tuple(book.items()) for book in allowed_books}]

    return allowed_books
