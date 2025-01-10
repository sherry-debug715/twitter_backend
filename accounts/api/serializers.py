from django.contrib.auth.models import User 
from rest_framework import serializers 


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User 
        fields = ("id", "username", "email")


class LoginSerializer(serializers.Serializer):
    # make sure login request has username and password 
    username = serializers.CharField()
    password = serializers.CharField()