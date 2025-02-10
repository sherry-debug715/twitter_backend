from testing.testcase import TestCase 
from rest_framework.test import APIClient
from django.utils import timezone
from comments.models import Comment

COMMENT_URL = "/api/comments/"
TWEET_LIST_API = "/api/tweets/"
TWEET_DETAIL_API = "/api/tweets/{}/"
NEWSFEED_LIST_API = "/api/newsfeeds/"

class CommentModelTests(TestCase):

    def setUp(self):
        self.sherry, self.sherry_client = self.create_user_and_client("sherry") 
        self.panda, self.panda_client = self.create_user_and_client("panda")

        self.tweet = self.create_tweet(self.sherry)
        self.comment = self.create_comment(self.sherry, self.tweet, "1")

    def test_comment_model(self):
        user = self.panda
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
        self.assertEqual(response.data["user"], self.sherry.id)
        self.assertEqual(response.data["tweet_id"], self.tweet.id)
        self.assertEqual(response.data["content"], "1")

    def test_update(self):
        comment = self.create_comment(self.sherry, self.tweet, "original comments")
        another_tweet = self.create_tweet(self.panda)
        url = "{}{}/".format(COMMENT_URL, comment.id)

        # An anonymous client can't edit a comment
        response = self.anonymous_client.put(url, {"content": "new"})
        self.assertEqual(response.status_code, 403)
        # A non comment creator can't edit the comment
        response = self.panda_client.put(url, {"content": "new"})
        self.assertEqual(response.status_code, 403)
        # Django doesn't automatically reload the instance from the database to reflect the changes after an update, calling refresh_from_db() tells Django to fetch the latest data from the database and update the current instance with the most recent values.
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, "new")

        # A user can only edit the comment content 
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.sherry_client.put(url, {
            "content": "new",
            "user_id": self.panda.id,
            "tweet_id": another_tweet.id,
            "created_at": now, 
        })

        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, "new")
        self.assertEqual(comment.user, self.sherry)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNoLogs(comment.updated_at, before_updated_at)
        self.assertNotEqual(comment.created_at, now)

    def test_destroy(self):
        comment = self.create_comment(self.sherry, self.tweet)
        url = "{}{}/".format(COMMENT_URL, comment.id)

        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # only the creator of the comment can delete 
        response = self.panda_client.delete(url)
        self.assertEqual(response.status_code, 403)

        count = Comment.objects.count()
        response = self.sherry_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_list(self):
        # withtout sending tweet_id
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code, 400) 

        # only one comment is created in setup
        response = self.anonymous_client.get(COMMENT_URL, {
            "tweet_id": self.tweet.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["comments"]), 1) 

        # returned comments should be ordered by created at descendingly 
        self.create_comment(self.sherry, self.tweet, "2")
        self.create_comment(self.panda,  self.tweet, "3")
        self.create_comment(self.sherry, self.create_tweet(self.panda), "3")
        response = self.anonymous_client.get(COMMENT_URL, {
            "tweet_id": self.tweet.id,
        })
        self.assertEqual(len(response.data["comments"]), 3)
        self.assertEqual(response.data["comments"][0]["content"], "1")
        self.assertEqual(response.data["comments"][1]["content"], "2")

        # when passed both tweet_id and user_id to param, only tweet_id will be recognized by django filter 
        response = self.anonymous_client.get(COMMENT_URL, {
            "tweet_id": self.tweet.id,
            "user_id": self.sherry.id,
        })

        self.assertEqual(len(response.data["comments"]), 3)

    def test_like_set(self):
        self.create_like(self.panda, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.panda, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.sherry, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)

    def test_comments_count(self):
        # test tweet detail api 
        tweet = self.create_tweet(self.sherry, "first tweet from sherry")
        tweet_detail_url = TWEET_DETAIL_API.format(tweet.id)
        response = self.panda_client.get(tweet_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["comments_count"], 0) 

        # test tweet list api 
        self.create_comment(self.panda, tweet, "first comment from panda to sherry tweet")
        response = self.panda_client.get(tweet_detail_url)
        response = self.panda_client.get(TWEET_LIST_API, {"user_id": self.sherry.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["tweets"][0]["comments_count"], 1)

        # test newsfeed list api 
        self.create_comment(self.sherry, tweet)
        self.create_newsfeed(self.panda, tweet)
        response = self.panda_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["newsfeeds"][0]["tweet"]["comments_count"], 2)






