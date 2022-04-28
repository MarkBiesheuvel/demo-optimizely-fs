from os import environ
from time import sleep
from random import randint
from logging import WARNING
from json import dumps as json_encode
from optimizely.optimizely import Optimizely
from optimizely.logger import NoOpLogger
from optimizely.event_dispatcher import EventDispatcher
from optimizely.event.event_processor import BatchEventProcessor
from dynamodb_user_profile import DynamodbUserProfile

if 'OPTIMIZELY_SDK_KEY' not in environ:
    exit('Environment variable "OPTIMIZELY_SDK_KEY" not set')

# Initiate Optimizely client
optimizely_client = Optimizely(
    sdk_key=environ['OPTIMIZELY_SDK_KEY'],
    logger=NoOpLogger(),
    user_profile_service=DynamodbUserProfile(),
    event_processor=BatchEventProcessor(
        EventDispatcher,
        batch_size=15,
        flush_interval=30,
        start_on_init=True
    ),
)

# TODO: replace with some dynamic content
products = [
    {
        'name': 'Logitech Wireless Mouse M705',
        'price': 39.99,
        'category': 'computer|mouse',
    },
    {
        'name': 'Gigabyte GeForce RTX 3060 Ti Eagle OC 8G rev. 2.0 LHR',
        'price': 729.00,
        'category': 'computer|gpu',
    },
    {
        'name': 'Elgato Stream Deck XL',
        'price': 244.99,
        'category': 'computer|accessories',
    },
    {
        'name': 'Logitech Spotlight',
        'price': 115.99,
        'category': 'computer|accessories',
    },
    {
        'name': 'Braun Series 9 Pro 9465cc',
        'price': 249.99,
        'category': 'care|shaving',
    },
    {
        'name': 'Sony KD-75XH9096',
        'price': 1888.99,
        'category': 'tv|led',
    },
    {
        'name': 'Sony HT-ZF9',
        'price': 499.00,
        'category': 'tv|speaker',
    },
    {
        'name': 'Vogel\'s Thin 550',
        'price': 295.00,
        'category': 'tv|bracket',
    },
]


def handler(event, context):
    # TODO: get user id from cookie
    user_id = str(randint(0, 25))

    # TODO: get attributes from request
    attributes = {
        'device': 'OnePlus 7 Pro',
        'country': 'NL',
    }

    # Get decision on a flag
    user = optimizely_client.create_user_context(user_id, attributes)
    decision = user.decide('sorting_algorithm')

    # Get variables from decision
    number_of_products = decision.variables['number_of_products']
    field = decision.variables['field']
    reverse = (decision.variables['direction'] == 'desc')

    # Sort and limit the products based on decision
    selected_products = sorted(
        products,
        key=lambda product: product[field],
        reverse=reverse
    )[:number_of_products]

    response = {
        'products': selected_products,
        'user_id': user_id,
        'variation': decision.variation_key,
        'variables': decision.variables,
    }

    # Return a HTTP response to API proxy
    return {
        'statusCode': 200,
        'multiValueHeaders': {
            'Set-Cookie': [
                'user_id={}; Max-Age=604800; Secure; HttpOnly; SameSite=Strict'.format(user_id)
            ],
        },
        'body': json_encode(response)
    }
