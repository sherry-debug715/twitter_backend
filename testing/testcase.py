from django.test import TestCase as DjangoTestCase 
from rest_framework.test import APIClient
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User 
from tweets.models import Tweet 
from comments.models import Comment
from likes.models import Like
from newsfeeds.models import NewsFeed


class TestCase(DjangoTestCase):

    @property
    def anonymous_client(self):
         # Check if the instance already has an attribute _anonymous_client
        if hasattr(self, "_anonymous_client"):
            # Return the existing _anonymous_client
            return self._anonymous_client 
        # Otherwise, create and store it
        self._anonymous_client = APIClient()
        # Return the new _anonymous_client
        return self._anonymous_client
    
    def create_user(self, username, email=None, password=None):
        if password is None:
            password = "password" 
        
        if email is None:
            email = "{}@gmail.com".format(username)

        return User.objects.create_user(username, email, password)

    def create_user_and_client(self, *args, **kwargs):
        user = self.create_user(*args, **kwargs)
        client = APIClient() 
        client.force_authenticate(user)
        return user, client 
    
    def create_tweet(self, user, content=None):
        if content is None:
            content = "default tweet content"
        
        return Tweet.objects.create(user=user, content=content)
    
    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = "default comments for tweet"
        return Comment.objects.create(user=user, tweet=tweet, content=content)
    
    def create_like(self, user, target):
        instance, _ = Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
            user=user,
        )
        return instance
    
    def create_newsfeed(self, user, tweet):
        return NewsFeed.objects.create(user=user, tweet=tweet)