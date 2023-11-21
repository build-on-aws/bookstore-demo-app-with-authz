import boto3
import json
import os
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from shared import get_user_claims

logger = Logger()
tracer = Tracer()

with open('database.json', 'r') as database:
    books = json.load(database)

HEADERS = {
    "Access-Control-Allow-Origin": os.environ.get("ALLOWED_ORIGIN"),
    "Access-Control-Allow-Headers": "Content-Type,Authorization,authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Access-Control-Allow-Credentials": True,
}

verified_permissions_client = boto3.client('verifiedpermissions')


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: LambdaContext):
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")

    source_ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp')
    jwt_token = event["headers"].get("Authorization")
    user_info = {"username": "Unknown", "role": "Unknown", "yearsAsMember": "Unknown", "region": "Unknown"}

    if jwt_token:
        user_info = get_user_claims(jwt_token, source_ip)

    logger.info(f"User info: {user_info}")
    product_list = []

    if user_info["role"] == 'Publisher' and user_info["username"] == 'Dante':
        # Handle batch authorization for publisher 'Dante'.
        product_list = handle_batch_is_authorized(user_info)
    else:
        # Construct the authorization request for other scenarios.
        authz_request = construct_authz_request(user_info)
        logger.info(f"Authorization request: {authz_request}")

        # Make the `is_authorized` call to Amazon Verified Permissions.
        response = verified_permissions_client.is_authorized(**authz_request)
        logger.info(f"Authorization response: {response}")

        # Determine which product list to return.
        product_list = determine_product_list(response, user_info)

    logger.info("Successfully returning product list")

    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps({"products": product_list}),
    }


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

    # For publishers, set the resource to their specific book.
    if user_info["role"] == 'Publisher':
        resource["entityId"] = "fn2padaa-c33l-4ea8-ll44-g7n217604p4n"
        entities.append(get_publisher_book_entity(user_info["username"]))

    # Determine action ID based on user role and yearsAsMember.
    action_id = "View"
    if user_info["role"] == 'Customer':
        years_as_member = user_info.get("yearsAsMember", 0)
        if years_as_member != "Unknown":
            action_id = "ViewPremiumOffers"
            entities[0]["attributes"]["yearsAsMember"] = {"long": int(years_as_member)}

    # Set `region` attribute in the context based on the specific user attributes.
    region = user_info.get('region', 'Unknown')
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


policies = {
    "PUBLISHERS_VIEW": "Allows publishers to see books they have published",
    "PUBLISHER_ACCESS_TO_ONE_BOOK": "Allows specific user to see a specific book",
    "PREMIUM_OFFERS": "Allows customers with specific value for yearsAsMember attribute to list premium offers",
    "NO_PREMIUM_OFFERS": "Denies customers with specific value for yearsAsMember attribute to list premium offers",
}


def get_publisher_book_entity(username):
    return {
        "identifier": {
            "entityType": "Bookstore::Book",
            "entityId": "fn2padaa-c33l-4ea8-ll44-g7n217604p4n"
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


def determine_product_list(response, user_info):
    if 'decision' in response:
        if response['decision'] == 'ALLOW':
            policy_description = get_policy_description(response)

            if user_info["role"] == 'Publisher' and policy_description == policies["PUBLISHERS_VIEW"]:
                # Return books published by this publisher.
                return [book for book in books['books'] if book['publisher'] == user_info['username']]

            # If allowed and not a publisher, return all books including premium offers.
            return books['books']
        elif response['decision'] == 'DENY':
            # Handle the deny decision for customers.
            if user_info["role"] == 'Customer':
                policy_description = get_policy_description(response)

                if policy_description == policies["NO_PREMIUM_OFFERS"]:
                    # Return regular books for customers without premium.
                    return [book for book in books['books'] if not book['premiumOffer']]

            return []  # Return an empty list for denied access.

    return books['books']  # Return all books if no specific policy applies.


def determine_product_list_for_publisher(responses, user_info):
    allowed_books = []

    for response in responses.get('results', []):
        if response.get('decision') == 'ALLOW':
            policy_description = get_policy_description(response)

            # Check if the policy allows the publisher to see the books they have published.
            # If not, check the other policy, if that allows a specific user to see a specific book.
            if policy_description == policies["PUBLISHERS_VIEW"]:
                allowed_books.extend([book for book in books['books'] if book['publisher'] == user_info['username']])
            elif policy_description == policies["PUBLISHER_ACCESS_TO_ONE_BOOK"]:
                book_id = response['request']['resource']['entityId']
                allowed_books.extend([book for book in books['books'] if book['id'] == book_id])

    # Remove duplicates, if any.
    allowed_books = [dict(t) for t in {tuple(book.items()) for book in allowed_books}]

    return allowed_books


def get_policy_description(response):
    logger.info(f"response info: {response}")
    policy_id = response.get('determiningPolicies', [{}])[0].get('policyId')

    if policy_id:
        policy_response = verified_permissions_client.get_policy(
            policyStoreId=os.environ.get("POLICY_STORE_ID"),
            policyId=policy_id
        )
        return policy_response.get('definition', {}).get('static', {}).get('description')

    return ""


def filter_books_based_on_policy(response, user_info, without_premium_offers=False):
    policy_description = get_policy_description(response)

    if policy_description == policies["PUBLISHERS_VIEW"]:
        return [book for book in books['books'] if book['publisher'] == user_info['username']]
    elif policy_description == policies["PREMIUM_OFFERS"]:
        return [book for book in books['books'] if book['premiumOffer']]
    elif policy_description == policies["NO_PREMIUM_OFFERS"] and without_premium_offers:
        # Return just regular books for customers without premium offers access.
        return [book for book in books['books'] if not book['premiumOffer']]
    elif user_info["role"] == 'Admin':
        # Assuming user with 'Admin' role can list all books.
        return books['books']
    else:
        return []


def handle_batch_is_authorized(user_info):
    batch_request = {
        'policyStoreId': os.environ.get("POLICY_STORE_ID"),
        'entities': {
            'entityList': [
                {
                    'identifier': {
                        'entityType': 'Bookstore::User',
                        'entityId': 'Dante'
                    },
                    'attributes': {},
                    'parents': [
                        {
                            'entityType': 'Bookstore::Role',
                            'entityId': 'Publisher'
                        }
                    ]
                },
                {
                    'identifier': {
                        'entityType': 'Bookstore::Book',
                        'entityId': 'em1oadaa-b22k-4ea8-kk33-f6m217604o3m'
                    },
                    'attributes': {
                        'owner': {
                            'entityIdentifier': {
                                'entityType': 'Bookstore::User',
                                'entityId': 'William'
                            }
                        }
                    },
                    'parents': []
                },
                {
                    'identifier': {
                        'entityType': 'Bookstore::Book',
                        'entityId': 'fn2padaa-c33l-4ea8-ll44-g7n217604p4n'
                    },
                    'attributes': {
                        'owner': {
                            'entityIdentifier': {
                                'entityType': 'Bookstore::User',
                                'entityId': 'Dante'
                            }
                        }
                    },
                    'parents': []
                }
            ]
        },
        'requests': [
            {
                'principal': {
                    'entityType': 'Bookstore::User',
                    'entityId': 'Dante'
                },
                'action': {
                    'actionType': 'Bookstore::Action',
                    'actionId': 'View'
                },
                'resource': {
                    'entityType': 'Bookstore::Book',
                    'entityId': 'em1oadaa-b22k-4ea8-kk33-f6m217604o3m'
                },
                'context': {
                    'contextMap': {
                        'region': {
                            'string': 'US'
                        }
                    }
                }
            },
            {
                'principal': {
                    'entityType': 'Bookstore::User',
                    'entityId': 'Dante'
                },
                'action': {
                    'actionType': 'Bookstore::Action',
                    'actionId': 'View'
                },
                'resource': {
                    'entityType': 'Bookstore::Book',
                    'entityId': 'fn2padaa-c33l-4ea8-ll44-g7n217604p4n'
                },
                'context': {
                    'contextMap': {
                        'region': {
                            'string': 'US'
                        }
                    }
                }
            }
        ]
    }

    # Call `batch_is_authorized` with the batch request.
    responses = verified_permissions_client.batch_is_authorized(**batch_request)
    logger.info(f"Bulk authorization response: {responses}")

    return determine_product_list_for_publisher(responses, user_info)
