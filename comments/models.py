from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User 
from tweets.models import Tweet 
from likes.models import Like


class Comment(models.Model):
    """
    User can comment on a tweet
    User can't comment on other user's comment
    """

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    tweet = models.ForeignKey(Tweet, null=True, on_delete=models.SET_NULL)
    content = models.TextField(max_length=140)
    # auto_now_add: This option automatically sets the field to the current timestamp only when the object is created.
    created_at = models.DateTimeField(auto_now_add=True)
    # auto_now: This option automatically sets the field to the current timestamp every time the object is saved (not just created).
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["tweet", "created_at"]),
        ]

    def __str__(self):
        return "{} - {} says {} at tweet {}".format(self.created_at, self.user, self.content, self.tweet_id)
    
    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.id,
        ).order_by("-created_at")
