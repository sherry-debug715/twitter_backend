"""
URL configuration for twitter project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include 
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from accounts.api.views import UserViewSet, AccountViewSet, UserProfileViewSet 
from tweets.api.views import TweetViewSet
from friendships.api.views import FriendshipViewSet
from newsfeeds.api.views import NewsFeedViewSet
from comments.api.views import CommentViewSet
from likes.api.views import LikeViewSet


router = routers.DefaultRouter()
router.register(r"api/users", UserViewSet)
router.register(r"api/accounts", AccountViewSet, basename="accounts")
router.register(r"api/tweets", TweetViewSet, basename="tweets")
router.register(r"api/friendships", FriendshipViewSet, basename="friendships")
router.register(r"api/newsfeeds", NewsFeedViewSet, basename="newsfeeds")
router.register(r"api/comments", CommentViewSet, basename="comments")
router.register(r"api/likes", LikeViewSet, basename="likes")
router.register(r"api/profiles", UserProfileViewSet, basename="profiles")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(
        path("__debug__", include(debug_toolbar.urls))
    )
