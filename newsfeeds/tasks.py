from celery import shared_task 
from friendships.services import FriendshipService 
from newsfeeds.constants import FANOUT_BATCH_SIZE
from newsfeeds.models import NewsFeed 
from tweets.models import Tweet 
from utils.time_constants import ONE_HOUR 

#The routing_key="newsfeed" means that this task will be routed to the queue associated with the routing key "newsfeed"
@shared_task(routing_key="newsfeed", time_limit=ONE_HOUR)
def fanout_newsfeeds_batch_task(tweet_id, follower_ids):
    # include import within the function to avoid infinite looping 
    from newsfeeds.services import NewsFeedService 

    # Correct method, using bulk create 
    newsfeeds = [
        NewsFeed(user_id=follower_id, tweet_id=tweet_id) 
        for follower_id in follower_ids
    ]
    NewsFeed.objects.bulk_create(newsfeeds)

    # save to cache 
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)

    return "{} newsfeeds created".format(len(newsfeeds))

@shared_task(routing_key="default", time_limit=ONE_HOUR)
def fanout_newsfeeds_main_task(tweet_id, tweet_user_id):
    # tweet creator should see the new tweet first 
    NewsFeed.objects.create(user_id=tweet_user_id, tweet_id=tweet_id)

    # get all follower ids, separate them according to the batch size 
    follower_ids = FriendshipService.get_follower_ids(tweet_user_id)
    index = 0
    batch_size = 0
    while index < len(follower_ids):
        batch_ids = follower_ids[index : index + FANOUT_BATCH_SIZE]
        """
        Asynchronous Execution: The delay method puts the task into the task queue. Celery workers (which are running separately) will pick up this task and execute it when they have available resources.

        Non-blocking: Calling delay does not block the main program. Your main code (like in the fanout_newsfeeds_main_task function) can continue executing while the task is being handled in the background.

        Arguments: The arguments passed to delay (in this case, tweet_id and batch_ids) are automatically serialized and sent to the queue, where Celery workers can pick them up and use them for processing.
        """
        fanout_newsfeeds_batch_task.delay(tweet_id, batch_ids)
        index += FANOUT_BATCH_SIZE 
        batch_size += 1
    
    return "{} newsfeeds going to fanout, {} batches created.".format(
        len(follower_ids),
        batch_size,
    )
