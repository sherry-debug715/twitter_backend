from django.db import models

from django.db import models 
from django.contrib.auth.models import User 
from tweets.models import Tweet 


class NewsFeed(models.Model):
    # user: when a user followed the tweet owner, the user can view the tweet
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # speed up query 
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]
        # makes sure a user with a tweet can't apear more than once
        unique_together = (("user", "tweet"),)
        ordering = ("user", "-created_at",)
    
    def __str__(self):
        return "{} inbox of {}: {}".format(self.created_at, self.user, self.tweet)
