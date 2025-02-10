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
    

class TweetSerializerWithComments(TweetSerializer):
    # In Django, when you define a reverse relationship (such as Comment related to Tweet), Django automatically creates a related manager on the Tweet model. By default, this related manager is named <model_name>_set (where model_name is the lowercase name of the related model, in this case, comment).
    # The source="comment_set" tells Django to use the comment_set related manager to retrieve all comments associated with the Tweet instance. The many=True argument tells Django that there could be multiple comments, so it will serialize them as a list.
    comments = CommentSerializer(source="comment_set", many=True)
    likes = LikeSerializer(source="like_set", many=True)

    class Meta:
        model = Tweet
        fields = ("id", "user", "comments", "created_at", "content", "likes", "likes_count", "comments_count", "has_liked")