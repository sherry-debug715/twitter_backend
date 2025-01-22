from rest_framework import viewsets, status 
from rest_framework.decorators import action 
from rest_framework.permissions import IsAuthenticated, AllowAny 
from rest_framework.response import Response 
from friendships.models import Friendship 
from .serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerializerForCreate,
)

from django.contrib.auth.models import User 

class FriendshipViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()

    @action(methods=["GET"], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        friendships = Friendship.objects.filter(to_user_id=pk).order_by("-created_at")
        serializer = FollowerSerializer(friendships, many=True)
        return Response(
            {"followers": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    @action(methods=["GET"], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by("-created_at")
        # With many=True (Serializing a list of objects)
        serializer = FollowingSerializer(friendships, many=True)
        return Response(
            {"followings": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # handling repeat follow, for example, follow button pressed multiple times 
        if Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
            return Response({
                "success": True,
                "duplicate": True,
            }, status=status.HTTP_201_CREATED)
        
        serializer = FriendshipSerializerForCreate(data={
            "from_user_id": request.user.id,
            "to_user_id": pk,
        })

        if not serializer.is_valid():
            return Response({
                "success": False,
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({
            "success": True,
        }, status=status.HTTP_201_CREATED)
    
    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        # pk is a str, need to be converted to int
        if request.user.id == int(pk):
            return Response({
                "success": False,
                "message": "You cannot unfollow yourself",
            }, status=status.HTTP_400_BAD_REQUEST)

        # delete() returns two data, 1, how many data is removed; 2. how many of each type of data is removed 
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=pk,
        ).delete()
        return Response({"success": True, "deleted": deleted})
    
    def list(self, request):
        return Response({"message": "this is friendships home page"})
        



        
