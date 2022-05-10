from json import dumps as json_encode
from random import randint
from os import environ
from optimizely.optimizely import Optimizely
from optimizely.logger import NoOpLogger

# Initiate Optimizely client
optimizely_client = Optimizely(
    sdk_key=environ['OPTIMIZELY_SDK_KEY'],
    logger=NoOpLogger(),
)


def add_cookie(cookies, key, value):
    cookies.append('{}={}; Max-Age=604800; Secure; HttpOnly; SameSite=Strict'.format(key, value))


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
    add_cookie(cookies, 'Optimizely-Variartion-Key', decision.variation_key)
    add_cookie(cookies, 'Optimizely-Variables', decision.variables)
    add_cookie(cookies, 'Optimizely-User-Id', user_id)

    # Return a HTTP response to API proxy
    return {
        'statusCode': 200,
        'multiValueHeaders': {
            'Set-Cookie': cookies,
        },
        'body': 'OK'
    }
