from optimizely.user_profile import UserProfileService
from boto3 import resource
from os import environ

if 'TABLE_NAME' not in environ:
    exit('Environment variable "TABLE_NAME" not set')

table = resource('dynamodb').Table(environ['TABLE_NAME'])


class DynamodbUserProfile(UserProfileService):

    def lookup(self, user_id):
        response = table.get_item(
            ConsistentRead=True,
            Key={
                'user_id': user_id,
            }
        )

        return response.get('Item', None)

    def save(self, user_profile):
        table.put_item(
            Item=user_profile,
            ReturnValues='NONE',
        )
