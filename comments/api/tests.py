from testing.testcase import TestCase 
from rest_framework.test import APIClient

COMMENT_URL = "/api/comments/"

class CommentModelTests(TestCase):

    def setUp(self):
        self.sherry = self.create_user("sherry")
        self.sherry_client = APIClient()
        self.sherry_client.force_authenticate(self.sherry)

        self.panda = self.create_user("panda")
        self.panda_client = APIClient()
        self.panda_client.force_authenticate(self.panda)

        self.create_tweet(self.sherry)

    def test_comment_model(self):
        user = self.create_user("sherry")
        tweet = self.create_tweet(user)
        comment = self.create_comment(user, tweet)
        self.assertNotEqual(comment.__str__(), None)

    def test_create_comment(self):
        # anoymous user can create comment 
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403) 

        # can't create without contents
        response = self.sherry_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        response = self.sherry_client.post(COMMENT_URL, {"tweet_id": self.tweet.id})
        self.assertEqual(response.status_code, 400)

        response = self.sherry_client.post(COMMENT_URL, {"content": "anything"})
        self.assertEqual(response.status_code, 400)

        #content too long 
        response = self.sherry_client.post(COMMENT_URL, {
            "tweet_id": self.tweet.id,
            "content": "1" * 141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual("content" in response.data["errors"], True)

        # successful 
        response = self.sherry_client.post(COMMENT_URL, {
            "tweet_id": self.tweet.id,
            "content": "1",
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"]["id"], self.sherry.id)
        self.assertEqual(response.data["tweet_id"], self.tweet.id)
        self.assertEqual(response.data["content"], "1")


