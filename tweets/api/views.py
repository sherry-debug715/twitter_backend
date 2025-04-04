from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from tweets.models import Tweet 
from .serializers import (
    TweetSerializer, 
    TweetCreateSerializer,
    TweetSerializerForDetail,    
)
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params
"""
GET /api/tweets/ → calls the list() method
GET /api/tweets/{id}/ → calls the retrieve() method (as in your case)
POST /api/tweets/ → calls the create() method
PUT /api/tweets/{id}/ → calls the update() method
DELETE /api/tweets/{id}/ → calls the destroy() method
"""

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
        serializer = TweetSerializer(
            tweets, 
            context={"request": request},
            many=True
        )

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
            error_msg = serializer.errors.get("non_field_errors", ["Please check input"])[0]
            return Response({
                "success": False,
                "message": error_msg,
                "errors": serializer.errors,
            }, status=400) 
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        serializer = TweetSerializer(tweet, context={"request": request})
        return Response(serializer.data, status=201)
    
    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        serializer =  TweetSerializerForDetail(
            tweet,
            context={"request": request},
        )
        return Response(serializer.data)