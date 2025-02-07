from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from newsfeeds.models import NewsFeed
from .serializers import NewsFeedSerializer




class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # only return the current logged in user newsfeed 
        return NewsFeed.objects.filter(user=self.request.user) 
    
    def list(self, request):
        serializer = NewsFeedSerializer(self.get_queryset(), many=True)
        return Response({
            "newsfeeds": serializer.data,
        }, status=status.HTTP_200_OK) 
