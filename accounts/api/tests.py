from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User 


LOGIN_URL = "/api/accounts/login/"
LOGOUT_URL = "/api/accounts/logout/"
SIGNUP_URL = "/api/accounts/signup/"
LOGIN_STATUS_URL = "/api/accounts/login_status/"


class AccountApiTests(TestCase):

    def setUp(self): # invoked everytime AccountApiTests runs 
        self.client = APIClient()
        self.user = self.create_user(
            username="test_user",
            email="test_user@gamil.com",
            password="password"
        )
    
    def create_user(self, username, email, password):
        # use create_user to encrypt password 
        return User.objects.create_user(username, email, password) 
    
    # every test method need to start with test_ 
    def test_login(self):
        # Test1: incorrect HTTP method -> 405 method not allowed 
        response = self.client.get(LOGIN_URL, {
            "username": self.user.username,
            "password": "password"
        })
        self.assertEqual(response.status_code, 405) 

        # Test2: wrong password -> 400 Bad request 
        response = self.client.post(LOGIN_URL, {
            "username": self.user.username,
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 404) 

        # Test3: test login_status api -> False  
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data["has_logged_in"], False)

        # Test4: test log in with correct credential 
        response = self.client.post(LOGIN_URL, {
            "username": self.user.username,
            "password": "password"
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data["user"], None)
        self.assertEqual(response.data["user"]["email"], "test_user@gamil.com") 

        # Test5: Recheck login status -> True 
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data["has_logged_in"], True)

    def test_logout(self):
        # Login 
        self.client.post(LOGIN_URL, {
            "username": self.user.username,
            "password": "password"
        })

        # Test 1: test login status 
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data["has_logged_in"], True) 

        # Test 2: logout http method has to be POST 
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405) 

        # Test 3: logout 
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        # Test 4: test login status to be logout 
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data["has_logged_in"], False) 

    def test_signup(self):
        data = {
            "username": "newuser",
            "email": "newuser@gmail.com",
            "password": "password"
        }

        # Test 1: sign up http method has to be POST
        response = self.client.get(SIGNUP_URL)
        self.assertEqual(response.status_code, 405) 

        # Test 2: wrong email 
        response = self.client.post(SIGNUP_URL, {
            "username": "newuser",
            "email": "wrong gmail",
            "password": "password"
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400) 

        # Test 3: password input < 6 
        response = self.client.post(SIGNUP_URL, {
            "username": "newuser",
            "email": "newuser@gmail.com",
            "password": "123"
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400) 

        # Test 3: username > 20
        response = self.client.post(SIGNUP_URL, {
            "username": "newusernewusernewusernewusernewusernewuser",
            "email": "newuser@gmail.com",
            "password": "password"
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400) 

        # Test 4: sign up successful 
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201) 
        self.assertEqual(response.data["user"]["username"], "newuser")
        self.assertEqual(response.data["user"]["email"], "newuser@gmail.com")

        # Test 5: test login status to be True 
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data["has_logged_in"], True) 







    


