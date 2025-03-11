from rest_framework import serializers

from accounts.api.serializers import UserSerializerForTweet 
from comments.api.serializers import CommentSerializer
from tweets.models import Tweet 
from likes.services import LikeService
from likes.api.serializers import LikeSerializer


class TweetSerializer(serializers.ModelSerializer):
    # Without using UserSerializer, "user" returned is going to be an Integer. 
    user = UserSerializerForTweet()
    #  If the field you want to include in the serialized output is not directly present in the model but can be derived or computed, you can use SerializerMethodField
    has_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = ("id", "user", "created_at", "content", "comments_count", "likes_count", "has_liked")

    def get_has_liked(self, obj):
        login_user = self.context["request"].user
        return LikeService.has_liked(login_user, obj)
    
    def get_likes_count(self, obj):
        return obj.like_set.count()
    
    def get_comments_count(self, obj):
        return obj.comment_set.count()


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
    

class TweetSerializerForDetail(TweetSerializer):
    comments = CommentSerializer(source="comment_set", many=True)
    likes = LikeSerializer(source="like_set", many=True)
    
    class Meta:
        model = Tweet
        fields = (
            "id", 
            "user", 
            "created_at", 
            "content", 
            "comments", 
            "likes", 
            "comments_count", 
            "likes_count", 
            "has_liked"
            )
