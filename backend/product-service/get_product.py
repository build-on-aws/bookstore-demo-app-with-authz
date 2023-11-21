import json
import os
from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()

with open('database.json', 'r') as database:
    books = json.load(database)

HEADERS = {
    "Access-Control-Allow-Origin": os.environ.get("ALLOWED_ORIGIN"),
    "Access-Control-Allow-Headers": "Content-Type,Authorization,authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
}


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    """
    Return single product based on path parameter.
    """
    path_params = event["pathParameters"]
    book_id = path_params.get("book_id")

    logger.debug(f"Retrieving book ID: {book_id}")

    product = next(
        (book for book in books if book["id"] == book_id), None
    )

    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps({"product": product}),
    }
