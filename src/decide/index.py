from json import dumps as json_encode
from base64 import b64encode as base64_encode_bytes
from random import randint
from os import environ
from optimizely.optimizely import Optimizely
from optimizely.logger import NoOpLogger

# Initiate Optimizely client
optimizely_client = Optimizely(
    sdk_key=environ['OPTIMIZELY_SDK_KEY'],
    logger=NoOpLogger(),
)

def base64_encode(string):
    return base64_encode_bytes(string.encode()).decode()


def add_cookie(cookies, key, value):
    cookies.append('{}={}; Path=/; Max-Age=604800; Secure; HttpOnly; SameSite=Strict'.format(key, value))


def handler(event, context):
    # Generate a random user id
    # TODO: implement UUID
    user_id = str(randint(0, 25))

    # Collect attributes from request
    attributes = {}

    # Get decision from Optimizely
    user = optimizely_client.create_user_context(user_id, attributes)
    decision = user.decide('sorting_algorithm')

    # Add cookies to response
    cookies = []
    add_cookie(cookies, 'Optimizely-User-Id', user_id)
    add_cookie(cookies, 'Optimizely-Variation-Key', decision.variation_key)
    add_cookie(cookies, 'Optimizely-Variables', base64_encode(json_encode(decision.variables)))

    # Return a HTTP response to API proxy
    return {
        'statusCode': 302,
        'headers': {
            'Location': '/',
            'Cache-Control': 'no-store, no-cache',
        },
        'multiValueHeaders': {
            'Set-Cookie': cookies,
        },
        'body': 'OK'
    }
