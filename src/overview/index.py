from os import environ
from time import sleep
from random import randint
from logging import INFO
from json import dumps as json_encode
from optimizely.optimizely import Optimizely
from optimizely.logger import SimpleLogger
from optimizely.event_dispatcher import EventDispatcher
from optimizely.event.event_processor import BatchEventProcessor

# Enable event batching
batch_processor = BatchEventProcessor(
    EventDispatcher,
    batch_size=15,
    flush_interval=30,
    start_on_init=True
)

# Enable logging
simple_logger = SimpleLogger(min_level=INFO)

# Initiate Optimizely client
optimizely_client = Optimizely(
    sdk_key=environ['OPTIMIZELY_SDK_KEY'],
    logger=simple_logger,
    event_processor=batch_processor
)


def handler(event, context):
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
            'price': 244.99,
            'category': 'care|shaving',
        },
    ]

    # Return a HTTP response to API proxy
    return {
        'statusCode': 200,
        'multiValueHeaders': {
            'Set-Cookie': ['user_id=42; Max-Age=604800; Secure; HttpOnly; SameSite=Strict'],
        },
        'body': json_encode(products)
    }
