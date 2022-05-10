from json import dumps as json_encode
from random import randint


def add_header(headers, key, value):
    headers[key.lower()] = [
        {
            'key': key,
            'value': value,
        }
    ]


def handler(event, context):
    print(json_encode(event))

    request = event['Records'][0]['cf']['request']
    headers = request['headers']

    found_cookie = False

    if (found_cookie):
        # TODO: get user id from cookie
        user_id = str(randint(0, 25))

        # TODO: get variation and variables from cookie
        # Forward custom headers to the origin
        add_header(headers, 'Optimizely-Variartion-Key', 'variation_2')
        add_header(headers, 'Optimizely-Variables', json_encode({
            'direction': 'desc',
            'field': 'category',
            'number_of_products': 5,
        }))

        # Add request header so it can be used in viewer response
        add_header(headers, 'Optimizely-User-Id', user_id)
    else:
        # No cookie found, so we send the user to /decide to generate one
        request['uri'] = '/decide'
        request['method'] = 'GET'

    print(json_encode(request))
    # Return modified request object
    return request
