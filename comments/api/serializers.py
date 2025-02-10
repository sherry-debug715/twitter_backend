from accounts.api.serializers import UserSerializerForComments
from comments.models import Comment
from rest_framework import serializers 
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet 
from likes.services import LikeService

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializerForComments
    like_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "tweet_id", "user", "content", "created_at", "like_count", "has_liked",)

    def get_like_count(self, obj):
        return obj.like_set.count()
    
    def get_has_liked(self, obj):
        login_user = self.context["request"].user
        return LikeService.has_liked(login_user, obj)

    
class CommentSerializerForCreate(serializers.ModelSerializer):
    # if want to access user_id and tweet_id, we need to add them 
    # manually, by default, ModelSerializer only include user and tweet 

    tweet_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Comment 
        fields = ("content", "tweet_id", "user_id") 

    def validate(self, data):
        tweet_id = data["tweet_id"]
        if not Tweet.objects.filter(id=tweet_id).exists():
            raise ValidationError({
                "message": "tweet doesn't exist"
            })
        # validated data must be returned 
        return data 

    def create(self, validated_data):
        return Comment.objects.create(
            user_id=validated_data["user_id"],
            tweet_id=validated_data["tweet_id"],
            content=validated_data["content"]
        )
    

class CommentSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("content",)

    def update(self, instance, validated_data):
        instance.content = validated_data["content"]
        instance.save()
        return instance 