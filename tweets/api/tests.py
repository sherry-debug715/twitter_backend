from rest_framework.test import APIClient 

from testing.testcase import TestCase
from tweets.models import Tweet 


TWEET_LIST_API = "/api/tweets/"
TWEET_CREATE_API = "/api/tweets/"
TWEET_RETRIEVE_API = "/api/tweets/{}/"


class TweetApiTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user(
            "user1",
            "user1@gmail.com",
        )
        self.tweet1 = [
            self.create_tweet(self.user1)
            for _ in range(3)
        ]
        # force_authenticate() method simulates authenticated users without having to go through the login process in tests.
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1) 

        self.user2 = self.create_user(
            "user2",
            "user2@gmail.com",
        )
        self.tweet2 = [
            self.create_tweet(self.user2)
            for _ in range(2)
        ]

    def test_list_api(self):
        # TEST 1: making request without user_id
        response = self.anonymous_client.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, 400)

        # TEST 2: making successful request 
        response = self.anonymous_client.get(TWEET_LIST_API, {"user_id": self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["tweets"]), 3)
        response = self.anonymous_client.get(TWEET_LIST_API, {"user_id": self.user2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["tweets"]), 2)

        # TEST 3: checking query order 
        self.assertEqual(response.data["tweets"][0]["id"], self.tweet2[1].id)
        self.assertEqual(response.data["tweets"][1]["id"], self.tweet2[0].id)

    def test_create_api(self):
        # TEST 1: testing log in 
        response = self.anonymous_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 403) 

        # TEST 2: without content 
        response = self.user1_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 400) 

        # TEST 3: fail content length validation 
        # TOO SHORT
        response = self.user1_client.post(TWEET_CREATE_API, {"content": "123"})
        self.assertEqual(response.status_code, 400) 
        # TOO LONG 
        response = self.user1_client.post(TWEET_CREATE_API, {"content": "123" * 99})
        self.assertEqual(response.status_code, 400) 

        # TEST 4: success post 
        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(TWEET_CREATE_API, {
            "content": "Hello World, this is my first tweet",
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"]["id"], self.user1.id) 
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)

    def test_retrieve(self):
        # Tweet id -1 doesn't exist
        url = TWEET_RETRIEVE_API.format(-1)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 404)

        # New tweet should have 0 comment
        tweet = self.create_tweet(self.user1)
        url = TWEET_RETRIEVE_API.format(tweet.id)
        response = self.anonymous_client.get(url) 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["comments"]), 0)

        # Check if comments count is correct
        self.create_comment(self.user2, tweet, "panda is cute")
        self.create_comment(self.user1, tweet, "hmmmm")
        response = self.anonymous_client.get(url)
        self.assertEqual(len(response.data["comments"]), 2)





