from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType 
from likes.models import Like
from accounts.api.serializers import UserSerializerForLike
from comments.models import Comment 
from tweets.models import Tweet




class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializerForLike()

    class Meta:
        model = Like
        fields = ("user", "created_at")

class BaseLikeSerializerForCreateAndCancel(serializers.ModelSerializer):
    content_type = serializers.ChoiceField(choices=["comment", "tweet"])
    object_id = serializers.IntegerField()

    class Meta:
        model = Like 
        fields = ("content_type", "object_id")

    def _get_model_class(self, data):
        if data["content_type"] == "comment":
            return Comment 
        elif data["content_type"] == "tweet":
            return Tweet
        else:
            return None 
    
    def validate(self, data):
        model_class = self._get_model_class(data)
        if model_class is None:
            raise ValidationError(
                {"content_type": "Content type doesn't exist"}
            )
        
        liked_object = model_class.objects.filter(id = data["object_id"]).first()
        if liked_object is None:
            raise ValidationError(
                {"object_id": "object doesn't exist"}
            )
        
        return data 

class LikeSerializerForCreate(BaseLikeSerializerForCreateAndCancel):
    def create(self, validated_data):
        model_class = self._get_model_class(validated_data)
        instance, _ = Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=validated_data["object_id"],
            user=self.context["request"].user,
        )
        return instance
    

class LikeSerializerForCancel(BaseLikeSerializerForCreateAndCancel):
    def cancel(self):
        """
        cancel is a customized function, serializer.save() doesn't invoke this method, therefore,
        to invoke this method, serializer.cancel() need to be called
        """
        model_class = self._get_model_class(self.validated_data)
        Like.objects.filter(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id = self.validated_data["object_id"],
            user=self.context["request"].user,
        ).delete()




