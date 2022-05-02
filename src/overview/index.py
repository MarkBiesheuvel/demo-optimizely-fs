from json import dumps as json_encode, loads as json_decode

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
    decision = json_decode(headers['Optimizely-Decision'])

    # Get variables from decision
    number_of_products = decision['number_of_products']
    field = decision['field']
    reverse = decision['reverse']

    # Sort and limit the products based on decision
    selected_products = sorted(
        products,
        key=lambda product: product[field],
        reverse=reverse
    )[:number_of_products]

    response = {
        'products': selected_products,
        'decision': decision,
    }

    # Return a HTTP response to API proxy
    return {
        'statusCode': 200,
        'body': json_encode(response)
    }
