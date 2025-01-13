from django.db import models
from django.contrib.auth.models import User 

class Friendship(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="following_friendship_set",
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="follower_friendship_set",
    )
    created_at = models.DateTimeField(auto_now_add=True) 

    class Meta:
        indexes = [
            # get people I follows, ordered by created_at 
            models.Index(fields=["from_user_id", "created_at"]), 
            # get people who follows me, ordered by created_at 
            models.Index(fields=["to_user_id", "created_at"]), 
        ]
        constraints = [
            models.UniqueConstraint(fields=["from_user", "to_user"], name="unique_friendship"), # This means a user cannot follow the same person more than once.
        ]
    
    def __str__(self):
        return f"{self.from_user_id} followed {self.to_user_id}"
