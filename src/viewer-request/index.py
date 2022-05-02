from json import dumps as json_encode


def handler(event, context):
    request = event['Records'][0]['cf']['request']
    headers = request['headers']

    # TODO: add Optimizely SDK

    decision = {
        'number_of_products': 5,
        'field': 'price',
        'reverse': True,
    }

    headers['optimizely-decision'] = [
        {
            'key': 'Optimizely-Decision',
            'value': json_encode(decision)
        }
    ]

    return request
