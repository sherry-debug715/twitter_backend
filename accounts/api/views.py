from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import (
    logout as django_logout,
    authenticate as django_authenticate,
    login as django_login,
)

from .serializers import UserSerializer, LoginSerializer, SignupSerializer


class UserViewSet(
    viewsets.ModelViewSet
):  # ModelViewSet allows user to operate CRUD, can change it to ReadOnlyModelViewSet
    """
    API endpoint that allows users to be viewed or edited
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class AccountViewSet(viewsets.ViewSet):
    serializer_class = LoginSerializer

    @action(
        methods=["GET"], detail=False
    )  # when setting primary key or other params, detail need to be set to True
    def login_status(self, request):
        data = {
            "has_logged_in": request.user.is_authenticated,
            "ip": request.META["REMOTE_ADDR"]
        }
        if request.user.is_authenticated:
            data["user"] = UserSerializer(request.user).data
        return Response(data)  # Response default status code is 200

    @action(methods=["POST"], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({"sucess": True})

    @action(methods=["POST"], detail=False)
    def login(self, request):
        # get username and password from request
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Please check input",
                    "errors": serializer.errors,
                },
                status=400,
            )

        # pass validation, try login
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        user = django_authenticate(request, username=username, password=password)

        # if user is not registered
        if not user or user.is_anonymous:
            return Response(
                {"success": False, "message": "Username and password does not match"},
                status=404,
            )

        # User registered, login
        django_login(request, user)
        return Response({"success": True, "user": UserSerializer(user).data})

    @action(methods=["POST"], detail=False)
    def signup(self, request):
        serializer = SignupSerializer(data=request.data) # data key must exist 
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Please check input",
                    "errors": serializer.errors,
                },
                status=400,
            )

        user = serializer.save()
        django_login(request, user)
        return Response({"success": True, "user": UserSerializer(user).data}, status=201)
