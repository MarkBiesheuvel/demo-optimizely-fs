from os import environ
from random import randint
from optimizely import optimizely
from optimizely.config_manager import PollingConfigManager

# Initiate Optimizely client
optimizely_client = optimizely.Optimizely(
    config_manager=PollingConfigManager(
       sdk_key = environ['OPTIMIZELY_SDK_KEY'],
       update_interval=120,
    )
)

# Use hardcoded values for now
user_id = str(randint(0, 10))
attributes = {
  'device': 'OnePlus 7 Pro',
  'is_premium_member': True,
  'country': 'NL',
}

print('Current user is {}'.format(user_id))

# Create use in Optimizely
user = optimizely_client.create_user_context(user_id, attributes)

# Make decision
decision = user.decide('sorting_algorithm')
print('Selected variantion is `{}`'.format(decision.variation_key))


for variable, value in decision.variables.items():
    print('- Variable `{}` is `{}`'.format(variable, value))
