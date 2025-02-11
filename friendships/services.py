from friendships.models import Friendship 
from django.core.cache import caches
from django.conf import settings 
from twitter.cache import FOLLOWINGS_PATTERN

# cache = caches["testing"] if settings.TESTING else caches["default"]


class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        """
        Wrong method One: could cause N+1 Queries 
        By filtering out all friendships from Friendship cost one query.
        Use a for loop to iterate through all the friendships is N queries
        friendships = Friendship.objects.filter(to_user=user)
        return [friendship.from_user for friendship in friendships]
        """

        """
        Wrong method Two: Forbidden when having large amount of users, because it's really slow. select_related('from_user') tells Django to use a SQL JOIN between the Friendship table and the User table on the from_user field. This means that the result will include not only the Friendship rows where to_user=user, but also the associated User objects for each from_user in One query.

        friendships = Friendship.objects.filter(
            to_user=user
        ).select_related('from_user')
        return [friendship.from_user for friendship in friendships]
        """

        """
        Correct Method One: use IN QUERY
        friendships = Friendship.objects.filter(to_user=user)
        follower_ids = [friendship.from_user_id  for friendship in friendships]
        followers = User.objects.filter(id__in=follower_ids)
        
        """

        # prefetch_related is a method in Django's ORM used to optimize queries by reducing the number of database hits when retrieving related objects. It is particularly useful for Many-to-Many and reverse ForeignKey relationships.

        friendships = Friendship.objects.filter(to_user=user).prefetch_related("from_user")
        return [friendship.from_user for friendship in friendships]
    
    @classmethod
    def get_follower_ids(cls, to_user_id):
        friendships = Friendship.objects.filter(to_user_id=to_user_id)
        return [friendship.from_user_id for friendship in friendships]
    
  
