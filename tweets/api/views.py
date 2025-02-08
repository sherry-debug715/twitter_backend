from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from tweets.models import Tweet 
from .serializers import (
    TweetSerializer, 
    TweetCreateSerializer,
    TweetSerializerWithComments,    
)
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params

class TweetViewSet(viewsets.GenericViewSet):
    """
    API endpoint: create new tweet, view tweets 
    """
    serializer_class = TweetCreateSerializer
    queryset = Tweet.objects.all()

    def get_permissions(self):
        if self.action in ("list", "retrieve"): # self.action is referring to any instance method of TweetViewSet
            return [AllowAny()] # allow any user to view. 
        return [IsAuthenticated()] 
    
    @required_params(params=["user_id"])
    def list(self, request):
        # query tweets post by user_id from query_params, ordered by new to old 
        tweets = Tweet.objects.filter(
            user_id = request.query_params["user_id"]
        ).order_by("-created_at") # -> returns a QuerySet
        serializer = TweetSerializer(tweets, many=True)

        # return tweets in json format 
        return Response({"tweets": serializer.data})
    
    def create(self, request):
        """
        By default, use the login user as tweet.user 
        """
        serializer = TweetCreateSerializer(
            data=request.data,
            context={"request":request},
        )
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400) 
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet).data, status=201)
    
    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        return Response(TweetSerializerWithComments(tweet).data)