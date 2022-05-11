from json import dumps as json_encode, loads as json_decode
from base64 import b64decode as base64_decode_bytes
from http.cookies import SimpleCookie

# Default settings in case no data
DEFAULT_FIELD = 'price'
DEFAULT_DIRECTION = 'asc'
DEFAULT_NUMBER_OF_PRODUCTS = 3

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


def base64_decode(string):
    return base64_decode_bytes(string.encode()).decode()


def handler(event, context):
    print(json_encode(event))

    # Collect cookie data
    cookie = SimpleCookie()
    cookie.load(event['headers']['Cookie'])

    # Get decision from custom header
    variation_key = cookie.get('Optimizely-Variation-Key').value
    variables = json_decode(base64_decode(cookie.get('Optimizely-Variables').value))

    # Get variables from decision
    number_of_products = variables.get('number_of_products', DEFAULT_NUMBER_OF_PRODUCTS)
    field = variables.get('field', DEFAULT_FIELD)
    direction = variables.get('direction', DEFAULT_DIRECTION)

    # Sort and limit the products based on decision
    selected_products = sorted(
        products,
        key=lambda product: product[field],
        reverse=(direction == 'desc')
    )[:number_of_products]

    response = {
        'products': selected_products,
        'variation_key': variation_key,
        'variables': variables,
    }

    # Return a HTTP response to API proxy
    return {
        'statusCode': 200,
        'body': json_encode(response)
    }
