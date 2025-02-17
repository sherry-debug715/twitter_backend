from testing.testcase import TestCase 
from accounts.models import UserProfile 


class UserProfileTests(TestCase):

    def test_profile_property(self):
        sherry = self.create_user("sherry")
        self.assertEqual(UserProfile.objects.count(), 0)
        profile = sherry.profile
        self.assertEqual(isinstance(profile, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)