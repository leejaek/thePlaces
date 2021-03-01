import json
import bcrypt
import jwt

from django.test import TestCase, Client

from user.models import User
from local_settings import SECRET_KEY, ALGORITHM

class SignUpTest(TestCase):
    def tearDown(self):
        User.objects.all().delete()

    def test_signup(self):
        client = Client()
        data = {
                'email'    : 'test@test.com',
                'password' : 'Qwer1234!',
                'nickname' : 'testuser'
                }

        response = client.post('/user/signup', json.dumps(data), content_type='application/json')

        self.assertEquals(response.json(), {"message": "SUCCESS"})
        self.assertEquals(response.status_code, 201)


class SignInTest(TestCase):
    def setUp(self):
        hashed_password = bcrypt.hashpw('Qwer1234!'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        User.objects.create(
            email    = 'test@test.com',
            password = hashed_password,
            nickname = 'testuser'
        )

    def tearDown(self):
        User.objects.all().delete()

    def test_signin(self):
        client = Client()
        data = {
                'email'   : 'test@test.com',
                'password': 'Qwer1234!' 
        }

        response = client.post('/user/signin', json.dumps(data), content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json(), {'message': 'SUCCESS', 'access_token': response.json()['access_token']})
        
