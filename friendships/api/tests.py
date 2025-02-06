from friendships.models import Friendship
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.test import TestCase

FOLLOW_URL = "/api/friendships/{}/follow/"
UNFOLLOW_URL = "/api/friendships/{}/unfollow/"
FOLLOWERS_URL =  "/api/friendships/{}/followers/"
FOLLOWING_URL = "/api/friendships/{}/followings/" 


class FriendshipApiTests(TestCase):

    def setUp(self):
        self.anonymous_client = APIClient() 

        self.sherry = self.create_user("sherry")
        self.sherry_client = APIClient()
        self.sherry_client.force_authenticate(self.sherry)

        self.panda = self.create_user("panda")
        self.panda_client = APIClient()
        self.panda_client.force_authenticate(self.panda)

        # create followings and followers for panda 
        for i in range(2):
            follower = self.create_user("panda_follower{}".format(i))
            Friendship.objects.create(from_user=follower, to_user=self.panda)
        
        for i in range(3):
            following = self.create_user("panda_following{}".format(i))
            Friendship.objects.create(from_user=self.panda, to_user=following) 
    
    def create_user(self, user_name):
        return User.objects.create_user(user_name)
    
    def test_follow(self):
        url = FOLLOW_URL.format(self.sherry.id)

        # Test for authentication 
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # Wrong method to follow 
        response = self.panda_client.get(url)
        self.assertEqual(response.status_code, 405)
        # A user can't follow the userself 
        response = self.sherry_client.post(url)
        self.assertEqual(response.status_code, 400) 
        # follow successful 
        response = self.panda_client.post(url) 
        self.assertEqual(response.status_code, 201)
        # duplicate follow, handle silently 
        response = self.panda_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["duplicate"], True)

        count = Friendship.objects.count()
        response = self.sherry_client.post(FOLLOW_URL.format(self.panda.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.sherry.id)

        # Test for authentication 
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # http method can't be get
        response = self.panda_client.get(url)
        self.assertEqual(response.status_code, 405)
        # A user can not follow self 
        response = self.sherry_client.post(url)
        self.assertEqual(response.status_code, 400)
        # successful request 
        Friendship.objects.create(from_user=self.panda, to_user=self.sherry)
        count = Friendship.objects.count()
        response = self.panda_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["deleted"], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)
        # unfollow a not followed user handle silently 
        count = Friendship.objects.count()
        response = self.panda_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["deleted"], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWING_URL.format(self.panda.id)
        # POST method is not allowed 
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405) 
        # GET method is allowed 
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["followings"]), 3)

        # Check if returned data is sorted by created_at 
        ts0 = response.data["followings"][0]["created_at"]
        ts1 = response.data["followings"][1]["created_at"]
        ts2 = response.data["followings"][2]["created_at"]
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data["followings"][0]["user"]["username"], "panda_following2"
        )
        self.assertEqual(
            response.data["followings"][1]["user"]["username"], "panda_following1"
        )
        self.assertEqual(
            response.data["followings"][2]["user"]["username"], "panda_following0"
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.panda.id)
        # POST method is not allowed 
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405) 
        # GET method is allowed 
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["followers"]), 2)
        # Check if returned data is sorted by created_at 
        ts0 = response.data["followers"][0]["created_at"]
        ts1 = response.data["followers"][1]["created_at"]
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data["followers"][0]["user"]["username"], "panda_follower1"
        )
        self.assertEqual(
            response.data["followers"][1]["user"]["username"], "panda_follower0"
        )



