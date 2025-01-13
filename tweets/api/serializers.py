from rest_framework import serializers

from accounts.api.serializers import UserSerializerForTweet 
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