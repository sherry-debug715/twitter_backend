from django.contrib.auth.models import User
from rest_framework import serializers, exceptions
from accounts.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")

    
class UserSerializerWithProfile(UserSerializer):
    nickname = serializers.CharField(source="profile.nickname")
    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        if obj.profile.avatar:
            return obj.profile.avatar.url
        return None 
    
    class Meta:
        model = User 
        fields = ("id", "username", "nickname", "avatar_url")


class UserSerializerForTweet(UserSerializerWithProfile):
    pass


class UserSerializerForComments(UserSerializerWithProfile):
    pass


class UserSerializerForFriendship(UserSerializerWithProfile):
    pass


class UserSerializerForLike(UserSerializerWithProfile):
    pass


class UserProfileSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("nickname", "avatar")


class LoginSerializer(serializers.Serializer):
    # make sure login request has username and password
    username = serializers.CharField()
    password = serializers.CharField()


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()


    class Meta:
        model = User
        fields = ("username", "email", "password")

    def validate(self, data):
        if User.objects.filter(username=data["username"].lower()).exists():
            raise exceptions.ValidationError(
                {"message": "This username has been occupied."}
            )
        if User.objects.filter(email=data["email"].lower()).exists():
            raise exceptions.ValidationError(
                {"message": "This email address has been occupied"}
            )

        return data

    def create(self, validate_data):
        username = validate_data["username"].lower()
        email = validate_data["email"].lower()
        password = validate_data["password"]

        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        # Create user profile
        user.profile
        return user
