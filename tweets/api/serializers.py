from rest_framework import serializers

from accounts.api.serializers import UserSerializerForTweet 
from comments.api.serializers import CommentSerializer
from tweets.models import Tweet 


class TweetSerializer(serializers.ModelSerializer):
    # Without using UserSerializer, "user" returned is going to be an Integer. 
    user = UserSerializerForTweet()

    class Meta:
        model = Tweet
        fields = ("id", "user", "created_at", "content",)


class TweetCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)

    class Meta:
        model = Tweet
        fields =("content",) 

    def create(self, validated_data):
        user = self.context["request"].user 
        content = validated_data["content"]
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet
    

class TweetSerializerWithComments(serializers.ModelSerializer):
    user = UserSerializerForTweet()
    # In Django, when you define a reverse relationship (such as Comment related to Tweet), Django automatically creates a related manager on the Tweet model. By default, this related manager is named <model_name>_set (where model_name is the lowercase name of the related model, in this case, comment).
    # The source="comment_set" tells Django to use the comment_set related manager to retrieve all comments associated with the Tweet instance. The many=True argument tells Django that there could be multiple comments, so it will serialize them as a list.
    comments = CommentSerializer(source="comment_set", many=True)

    class Meta:
        model = Tweet
        fields = ("id", "user", "comments", "created_at", "content")