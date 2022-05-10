from json import dumps as json_encode, loads as json_decode

# Default settings in case no data
EMPTY_OBJECT = '{}'
DEFAULT_VARIATION_KEY = 'off'
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


def handler(event, context):
    headers = event['headers']

    # Get decision from custom header
    variation_key = headers.get('Optimizely-Variartion-Key', DEFAULT_VARIATION_KEY)
    variables = json_decode(headers.get('Optimizely-Variables', EMPTY_OBJECT))

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
