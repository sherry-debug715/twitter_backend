from django.db import models
from django.contrib.auth.models import User 
from django.contrib.contenttypes.models import ContentType
from utils.time_helpers import utc_now 
from likes.models import Like


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]
        ordering = ("user", "-created_at")

    @property
    def hours_to_now(self):
        # datetime.now doesn't have time zone information, therefore using utc_now()
        return (utc_now() - self.created_at).seconds // 3600
    
    def __str__(self):
        return f"{self.created_at} {self.user}: {self.content}"
    
    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by("-created_at")
