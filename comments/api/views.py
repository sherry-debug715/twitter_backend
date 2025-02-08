from rest_framework import viewsets, status 
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated, AllowAny
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from comments.api.permissions import IsObjectOwner
from utils.decorators import required_params



class CommentViewSet(viewsets.GenericViewSet):

    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ("tweet_id",)

    # POST /api/comments/ -> create
    # GET /api/comments/ -> list
    # GET /api/comments/1/ -> retrieve 
    # DELETE /api/comments/1/ -> destroy
    # PATCH or PUT /api/comments/1/ -> update

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        if self.action in ["destroy", "update"]:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()] 
    
    @required_params(params=["tweet_id"])
    def list(self, request, *args, **kwargs):
        # When you call self.get_queryset(), it starts by looking at self.queryset (if it's defined) and returns it as a queryset object that you can then modify or filter further.
        queryset = self.get_queryset()
        comments = self.filter_queryset(queryset).order_by("created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(
            {"comments": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    def create(self, request, *args, **kwargs):
        data = {
            "user_id": request.user.id,
            "tweet_id": request.data.get("tweet_id"),
            "content": request.data.get("content"),
        }

        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # save method will invoke create method from CommentSerializerForCreate
        new_comment = serializer.save()
        return Response(
            CommentSerializer(new_comment).data,
            status=status.HTTP_201_CREATED,
        )
    
    def update(self, request, *args, **kwargs):
        # get_object is built into DRF viewsets.GenericViewSet, if it can't find the object, it will raise 404 error.
        serializer = CommentSerializerForUpdate(
            instance=self.get_object(),
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST) 
        
        # here save method will invoke the update method of CommentSerializerForUpdate, save will decide whether to invoke create method or update method based on the instance
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_200_OK,
        )
    
    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        # DRF destroy default return code is 204 no content, return success=True will help the frontend see clearly that the delete is successful 
        return Response({"success": True}, status=status.HTTP_200_OK)
