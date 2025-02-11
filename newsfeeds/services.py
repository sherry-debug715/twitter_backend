from newsfeeds.models import NewsFeed
from newsfeeds.tasks import fanout_newsfeeds_main_task 
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_helper import RedisHelper


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        """
        Wrong method
        can not keep database operation inside a for loop, low efficiency 

        for follower in FriendshipService.get_followers:
            NewsFeed.objects.create(
                user=follower,
                tweet=tweet,
            )
        """

        # Correct method, using bulk create 
        fanout_newsfeeds_main_task.delay(tweet.id, tweet.user_id) 

    
    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        queryset = NewsFeed.object.filter(user_id=newsfeed.user_id).order_by("-created_at")
        key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        return RedisHelper.load_objects(key, queryset)
