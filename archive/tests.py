import json
import bcrypt
import jwt
from datetime import timedelta

from django.test import TestCase, Client
from django.utils import timezone

from .models import CheckIn
from place.models import MetroRegion, LocalRegion, PlaceType, Place
from user.models import User

from local_settings import SECRET_KEY, ALGORITHM

class CheckInTest(TestCase):
    def setUp(self):
        test_metro   = MetroRegion.objects.create(name='테스트광역시')
        test_local   = LocalRegion.objects.create(name='테스트구', metro_region=test_metro)
        test_type    = PlaceType.objects.create(name='테스트타입')
        test_place   = Place.objects.create(id = 1, place_type = test_type, region = test_local, road_address = '테스트로 1', name = '테스트')

        hashed_password     = bcrypt.hashpw('Qwer1234!'.encode('utf-8'), bcrypt.gensalt()).decode()
        
        # Create Test
        test_user           = User.objects.create(email = 'test@test.com', password = hashed_password, nickname = 'testuser')
        self.token           = jwt.encode({'id': test_user.id, 'exp': timezone.now() + timedelta(hours = 24)}, SECRET_KEY, algorithm=ALGORITHM)

        # Create Duplicate Test
        test_user_duplicate = User.objects.create(email = 'duplicate@test.com', password = hashed_password, nickname = 'duplicattestuser')
        self.token_duplicate = jwt.encode({'id': test_user_duplicate.id, 'exp': timezone.now() + timedelta(hours = 24)}, SECRET_KEY, algorithm=ALGORITHM) 
        test_checkin = CheckIn.objects.create(user = test_user_duplicate, place = test_place, created_at = timezone.now())
        
        # Read and delete Test
        test_user_read   = User.objects.create(email = 'duplicate@test.com', password = hashed_password, nickname = 'deletetestuser')
        self.token_read  = jwt.encode({'id': test_user_read.id, 'exp': timezone.now() + timedelta(hours = 24)}, SECRET_KEY, algorithm=ALGORITHM)

        self.create_time = timezone.now()
        CheckIn.objects.create(id = 2, user = test_user_read, place = test_place, created_at = self.create_time)
        CheckIn.objects.create(id = 3, user = test_user_read, place = test_place, created_at = self.create_time, deleted_at = self.create_time)

    def tearDown(self):
        User.objects.all().delete()
        CheckIn.objects.all().delete()
        MetroRegion.objects.all().delete()
        LocalRegion.objects.all().delete()
        PlaceType.objects.all().delete()
        Place.objects.all().delete()

    def test_checkin_create(self):
        client = Client()
        header = {"HTTP_Authorization": self.token}

        response = client.post('/archive/checkin/place/1', **header, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "CHECKED_IN"})

    def test_checkin_create_duplicate(self):
        client = Client()
        header = {"HTTP_Authorization": self.token_duplicate}

        response = client.post('/archive/checkin/place/1', **header, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"message": "ALREADY_CHECKED_IN_TODAY"})


    def test_checkin_read(self):
        client  = Client()
        header  = {"HTTP_Authorization": self.token_read}


        response = client.get('/archive/checkin/place/1', **header, content_type='application/json')
        self.assertEqual(response.json(), {'result': [{'id':2, 'created_at': self.create_time.strftime('%Y-%m-%d')}]})
        self.assertEqual(response.status_code, 200)

    def test_checkin_delete_unauthorized(self):
        client = Client()
        header = {"HTTP_Authorization": self.token}
        
        response = client.delete('/archive/checkin/2', **header, content_type='application/json')
        self.assertEqual(response.json(), {"message": "UNAUTHORIZED"})
        self.assertEqual(response.status_code, 401)

    def test_checkin_delete(self):
        client  = Client()
        header  = {"HTTP_Authorization": self.token_read}
        
        response = client.delete('/archive/checkin/2', **header, content_type='appliation/json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(CheckIn.objects.get(id = 2).deleted_at == None, False)
    
    def test_checkin_invalid(self):
        client  = Client()
        header  = {"HTTP_Authorization": self.token_read}
        
        response = client.delete('/archive/checkin/3', **header, content_type='appliation/json')
        self.assertEqual(response.json(), {"message": "INVALID_CHECKIN"})
        self.assertEqual(response.status_code, 400)
    


