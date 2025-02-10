from testing.testcase import TestCase
from datetime import timedelta 
from utils.time_helpers import utc_now 
from utils.redis_client import RedisClient 
from utils.redis_serializers import DjangoModelSerializer 



class TweetTests(TestCase):
    def setUp(self):
        self.sherry = self.create_user(username="sherry")
        self.tweet = self.create_tweet(self.sherry)

    def test_hours_to_now(self):
        self.tweet.created_at = utc_now() - timedelta(hours=10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.sherry, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.sherry, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)


        self.panda = self.create_user("panda")
        self.create_like(self.panda, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)

    def test_cache_tweet_in_redis(self):
        tweet = self.create_tweet(self.sherry)
        conn = RedisClient.get_connection()
        serialized_tweet = DjangoModelSerializer.serialize(tweet)
        conn.set("tweet:{}".format(tweet.id), serialized_tweet)
        data = conn.get("tweet:not_exist")
        self.assertEqual(data, None) 

        data = conn.get("tweet:{}".format(tweet.id))
        cached_tweet = DjangoModelSerializer.deserialize(data)
        self.assertEqual(tweet, cached_tweet)


