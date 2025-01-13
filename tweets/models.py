from django.db import models
from django.contrib.auth.models import User 
from utils.time_helpers import utc_now 


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
