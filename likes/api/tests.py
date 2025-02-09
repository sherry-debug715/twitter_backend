from testing.testcase import TestCase 

LIKE_BASE_URL = "/api/likes/"
LIKE_CANCEL_URL = "/api/likes/cancel/"

class LikeApiTests(TestCase):

    def setUp(self):
        self.sherry, self.sherry_client = self.create_user_and_client("sherry")
        self.panda, self.panda_client = self.create_user_and_client("panda") 

    def test_tweet_likes(self):
        tweet = self.create_tweet(self.sherry) 
        data = {"content_type": "tweet", "object_id": tweet.id}

        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        response = self.panda_client.get(LIKE_BASE_URL, data) 
        self.assertEqual(response.status_code, 405) 

        response = self.panda_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 1)

        response = self.panda_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 1)

        self.sherry_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 2)

    def test_comment_likes(self):
        tweet = self.create_tweet(self.sherry) 
        comment = self.create_comment(self.panda, tweet)
        data = {"content_type": "comment", "object_id": comment.id}

        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        response = self.panda_client.get(LIKE_BASE_URL, data) 
        self.assertEqual(response.status_code, 405) 

        # wrong content_type
        response = self.sherry_client.post(LIKE_BASE_URL, {
            'content_type': 'coment',
            'object_id': comment.id,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content_type' in response.data['errors'], True)
 
        # wrong object id
        response = self.sherry_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': -3,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('object_id' in response.data['errors'], True)

        response = self.sherry_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)
        self.panda_client.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 2)

    def test_cancel(self):
        tweet = self.create_tweet(self.sherry)
        comment = self.create_comment(self.panda, tweet)
        like_comment_data = {"content_type": "comment", "object_id": comment.id}
        like_tweet_data = {"content_type": "tweet", "object_id": tweet.id}

        self.panda_client.post(LIKE_BASE_URL, like_tweet_data)
        self.assertEqual(tweet.like_set.count(), 1)
        self.sherry_client.post(LIKE_BASE_URL, like_comment_data)
        self.assertEqual(comment.like_set.count(), 1)

        # login required 
        response = self.anonymous_client.post(LIKE_BASE_URL, like_comment_data)
        self.assertEqual(response.status_code, 403)

        # get is not allowed 
        response = self.panda_client.get(LIKE_BASE_URL, like_tweet_data)
        self.assertEqual(response.status_code, 405)

        # wrong content type 
        response = self.panda_client.post(LIKE_BASE_URL, {
            "content_type": "twet",
            "object_id": tweet.id,
        })
        self.assertEqual(response.status_code, 400)

        # wrong object_id
        response = self.panda_client.post(LIKE_BASE_URL, {
            "content_type": "tweet",
            "object_id": -1,
        })
        self.assertEqual(response.status_code, 400)

        # successful cancel 
        response = self.panda_client.post(LIKE_CANCEL_URL, like_tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 0)

        response = self.sherry_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.like_set.count(), 0)