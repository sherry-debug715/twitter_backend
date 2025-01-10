from django.contrib.auth.models import User 
from django.contrib.auth import logout as django_logout
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet): # ModelViewSet allows user to operate CRUD, can change it to ReadOnlyModelViewSet
    """
    API endpoint that allows users to be viewed or edited 
    """

    queryset = User.objects.all().order_by("-date_joined") 
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class AccountViewSet(viewsets.ViewSet):
    serializer_class = UserSerializer

    @action(methods=["GET"], detail=False) # when setting primary key or other params, detail need to be set to True 
    def login_status(self, request):
        data = {"has_logged_in": request.user.is_authenticated}
        if request.user.is_authenticated:
            data["user"] = UserSerializer(request.user).data
        return Response(data)
    

    @action(methods=["POST"], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({"sucess": True})
