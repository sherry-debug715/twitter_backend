from newsfeeds.models import NewsFeed
from friendships.services import FriendshipService 


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
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet) 
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)