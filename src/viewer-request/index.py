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
    request = event['Records'][0]['cf']['request']
    headers = request['headers']

    # TODO: get user id from cookie
    user_id = str(randint(0, 25))

    # Collect attributes from CloudFront
    attributes = {
        '$opt_user_agent': headers.get('User-Agent', None),
        'is_premium_member': user_id.startswith('1'), # Deterministic (but seemingly random) boolean
        'country': headers.get('CloudFront-Viewer-Country', None),
        'is_desktop': headers.get('CloudFront-Is-Desktop-Viewer', False),
        'is_tablet': headers.get('CloudFront-Is-Tablet-Viewer', False),
        'is_mobile': headers.get('CloudFront-Is-Mobile-Viewer', False),
        'is_smarttv': headers.get('CloudFront-Is-SmartTV-Viewer', False),
        'is_android': headers.get('CloudFront-Is-Android-Viewer', False),
        'is_ios': headers.get('CloudFront-Is-IOS-Viewer', False),
    }

    # TODO: remove debug statements
    print(user_id)
    print(attributes)

    # TODO: find a way to get decision from data file within restrictions of Lambda@Edge
    print('Getting decision from Optimizely')

    '''IDEA:
    1) if no cookies set, forward entire request to origin (using different uri) and do not cache response
       at origin, a) set cookie with decision and user id using a custom userprofile service
                  b) redirect back to same page

    2) if cookies are set, forward only the variation information to origin and cache response
    '''

    # Forward custom headers to the origin
    add_header(headers, 'Optimizely-Variartion-Key', 'variation_2')
    add_header(headers, 'Optimizely-Variables', json_encode({
        'direction': 'desc',
        'field': 'category',
        'number_of_products': 5,
    }))

    # Add request header so it can be used in viewer response
    add_header(headers, 'Optimizely-User-Id', user_id)

    # Return modified request object
    return request
