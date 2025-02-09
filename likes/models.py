from django.db import models
from django.contrib.auth.models import User 
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType 
from django.db import models 


class Like(models.Model):
    # https://docs.djangoproject.com/en/3.1/ref/contrib/contenttypes/#generic-relations
    object_id = models.PositiveBigIntegerField()
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
    )
    content_object = GenericForeignKey("content_type", "object_id")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # unique_together: a user can only like a tweet or comment once 
        unique_together = ((
            "user",
            "content_type",
            "object_id",
        ))
        # indexes allows to get all likes of a tweet or comment sorted by created_at 
        indexes = [
            models.Index(fields=["content_type", "object_id", "created_at"]),
        ]

    def __str__(self):
        return "{} - {} liked {} {}".format(
            self.created_at,
            self.user,
            self.content_type,
            self.object_id,
        )
        