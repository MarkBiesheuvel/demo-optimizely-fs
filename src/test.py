from os import environ
from time import sleep
from random import randint
import logging
from optimizely import optimizely, logger, event_dispatcher
from optimizely.event import event_processor

# Enable event batching
batch_processor = event_processor.BatchEventProcessor(
    event_dispatcher.EventDispatcher,
    batch_size=15,
    flush_interval=30,
    start_on_init=True
)

# Enable logging
simple_logger = logger.SimpleLogger(min_level=logging.INFO)

# Initiate Optimizely client
optimizely_client = optimizely.Optimizely(
    sdk_key=environ['OPTIMIZELY_SDK_KEY'],
    logger=simple_logger,
    event_processor=batch_processor
)

for _ in range(120):

    # Use hardcoded values for now
    user_id = str(randint(0, 25))
    attributes = {
      'device': 'OnePlus 7 Pro',
      'is_premium_member': True,
      'country': 'NL',
    }

    # Create use in Optimizely
    user = optimizely_client.create_user_context(user_id, attributes)

    # Make decision
    decision = user.decide('sorting_algorithm')

    # Determine user action based on variation shown
    if (decision.variation_key == 'variantion_1'):
        tags = {
          'revenue': 69900,
          'category': 'computer|gpu'
        }
    else:
        tags = {
          'revenue': 2195,
          'category': 'computer|mouse'
        }

    # Track events
    user.track_event('purchase', {
      'revenue': 2195,
      'category': 'computer|mouse'
    })

    sleep(1)
