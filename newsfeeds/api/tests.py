from rest_framework.test import APIClient
from testing.testcase import TestCase 
from newsfeeds.models import NewsFeed
from friendships.models import Friendship
from testing.testcase import TestCase

NEWSFEEDS_URL = "/api/newsfeeds/"
POST_TWEETS_URL = "/api/tweets/"
FOLLOW_URL = "/api/friendships/{}/follow/"


class NewsFeedApiTest(TestCase):

    def setUp(self):
        self.sherry = self.create_user("sherry")
        self.sherry_client = APIClient()
        self.sherry_client.force_authenticate(self.sherry) 

        self.panda = self.create_user("panda")
        self.panda_client = APIClient()
        self.panda_client.force_authenticate(self.panda) 

        # create followers for panda 
        for i in range(2):
            follower = self.create_user("panda_follower{}".format(i))
            Friendship.objects.create(from_user=follower, to_user=self.panda)
        
        # create followings for panda 
        for i in range(3):
            following = self.create_user("panda_following{}".format(i))
            Friendship.objects.create(from_user=self.panda, to_user=following)
    
    def test_list(self):
        # Test 1: authentication 
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403) 

        # Test 2: POST method not allowed 
        response = self.panda_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405) 

        # Test 3: For a newly created user, newsfeeds is 0 
        response = self.panda_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["newsfeeds"]), 0)

        # Test 4: You get a news feed for your own newly created tweet 
        self.sherry_client.post(POST_TWEETS_URL, {
            "content": "Hello World"
        })
        response = self.sherry_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["newsfeeds"]), 1)
        self.assertEqual(response.data["newsfeeds"][0]["tweet"]["content"], "Hello World")

        # After user A follow user B, user A should be able to see user B's new tweet 
        self.sherry_client.post(FOLLOW_URL.format(self.panda.id))
        response = self.panda_client.post(POST_TWEETS_URL, {
            "content": "Hello news feed"
        }) 
        posted_tweet_id = response.data["id"]

        response = self.sherry_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["newsfeeds"]), 2)
        self.assertEqual(response.data["newsfeeds"][0]["tweet"]["id"], posted_tweet_id)
