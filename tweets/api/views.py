from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from tweets.models import Tweet 
from .serializers import TweetSerializer, TweetCreateSerializer


class TweetViewSet(viewsets.GenericViewSet):
    """
    API endpoint: create new tweet, view tweets 
    """
    serializer_class = TweetCreateSerializer

    def get_permissions(self):
        if self.action == "list": # self.action is referring to any instance method of TweetViewSet
            return [AllowAny()] # allow any user to view. 
        return [IsAuthenticated()] 
    
    def list(self, request):
        """
        Load lists, not required to list all tweets, must include user_ids in query params.
        """

        if "user_id" not in request.query_params:
            return Response("missing user_id", status=400)
        
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
        return Response(TweetSerializer(tweet).data, status=201)