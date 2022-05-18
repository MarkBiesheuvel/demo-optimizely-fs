import re

VARIATION_KEY_REGEX = re.compile('(^|; )Optimizely-Variation-Key=(\w+)(;|$)')


def contains_variation_key_cookie(request):
    headers = request['headers']

    # If no cookies are set at all, then the Variation-Key cookie definitly not set
    if not 'cookie' in headers:
        return False

    # Get the complete cookie string
    cookie = request['headers']['cookie'][0]['value']

    # Match the complete cookie string againt a regex to search for Variation-Key
    # TODO: validate whether the signature of the JWT token is valid
    return type(VARIATION_KEY_REGEX.search(cookie)) is re.Match


def handler(event, context):
    # Collect information from CloudFront event
    request = event['Records'][0]['cf']['request']

    # No cookie found, so we send the user to /decide to generate one
    if (not contains_variation_key_cookie(request)):
        # TODO: forward the original URI, so DecideFunction can redirect back
        request['uri'] = '/decide'
        request['method'] = 'GET'

    # Return modified request object
    return request
