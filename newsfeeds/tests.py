from newsfeeds.models import NewsFeed
from newsfeeds.tasks import fanout_newsfeeds_main_task 
from testing.testcase import TestCase 


class NewsFeedTaskTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.sherry = self.create_user("sherry")
        self.panda = self.create_user("panda")

    def test_fanout_main_task(self):
        tweet = self.create_tweet(self.sherry, "tweet 1")
        self.create_friendship(self.panda, self.sherry)
        msg = fanout_newsfeeds_main_task(tweet.id, self.sherry.id)
        self.assertEqual(msg, "1 newsfeeds going to fanout, 1 batches created.")
        self.assertEqual(1 + 1, NewsFeed.objects.count())
        
        for i in range(2):
            user = self.create_user("user{}".format(i))
            self.create_friendship(user, self.sherry)
        tweet = self.create_tweet(self.sherry, "tweet 2")
        msg = fanout_newsfeeds_main_task(tweet.id, self.sherry.id)
        self.assertEqual(msg, "3 newsfeeds going to fanout, 1 batches created.")
        self.assertEqual(2 + 4, NewsFeed.objects.count())

        user = self.create_user("another_user")
        self.create_friendship(user, self.sherry)
        tweet = self.create_tweet(self.sherry, "tweet 3")
        msg = fanout_newsfeeds_main_task(tweet.id, self.sherry.id)
        self.assertEqual(msg, "4 newsfeeds going to fanout, 1 batches created.")
        self.assertEqual(2 + 4 + 5, NewsFeed.objects.count())
        

