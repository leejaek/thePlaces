import json

from django.test import TestCase, Client
from django.utils import timezone

from .models import MetroRegion, LocalRegion, PlaceType, Place

class CreateTest(TestCase):
    def setUp(self):
        test_metro   = MetroRegion.objects.create(name='테스트광역시')
        test_local   = LocalRegion.objects.create(name='테스트구', metro_region=test_metro)
        test_type    = PlaceType.objects.create(name='테스트타입')
        test_place   = Place.objects.create(place_type = test_type, region = test_local, road_address = '중복테스트로 1', name = '중복테스트')
        test_place_2 = Place.objects.create(place_type = test_type, region = test_local, road_address = '중복테스트로 1', name = '중복테스트2', deleted_at = timezone.now())


    def tearDown(self):
        MetroRegion.objects.all().delete()
        LocalRegion.objects.all().delete()
        PlaceType.objects.all().delete()
        Place.objects.all().delete()

    def test_create(self):
        client = Client()
        data = {
                'place_type'   : '테스트타입',
                'metro_region' : '테스트광역시',
                'local_region' : '테스트구',
                'road_address' : '테스트로 327',
                'name'         : '테스트'
                }

        response = client.post('/place/', json.dumps(data), content_type='application/json')

        self.assertEquals(response.json(), {"message": "PLACE_CREATED"})
        self.assertEquals(response.status_code, 201)

    def test_address_format(self):
        client = Client()
        data = {
                'place_type'   : '테스트타입',
                'metro_region' : '테스트광역시',
                'local_region' : '테스트구',
                'road_address' : '테스트',
                'name'         : '테스트'
                }

        response = client.post('/place/', json.dumps(data), content_type='application/json')

        self.assertEquals(response.json(), {"message": "INVALID_ROAD_ADDRESS_FORMAT"})
        self.assertEquals(response.status_code, 400)

    def test_duplicate(self):
        client = Client()
        data = {
                'place_type'   : '테스트타입',
                'metro_region' : '테스트광역시',
                'local_region' : '테스트구',
                'road_address' : '중복테스트로 1',
                'name'         : '중복테스트'
                }

        response = client.post('/place/', json.dumps(data), content_type='application/json')

        self.assertEquals(response.json(), {"message": "EXIST_PLACE"})
        self.assertEquals(response.status_code, 400)

    def test_duplicate_2(self):
        client = Client()
        data = {
                'place_type'   : '테스트타입',
                'metro_region' : '테스트광역시',
                'local_region' : '테스트구',
                'road_address' : '중복테스트로 1',
                'name'         : '중복테스트2'
                }

        response = client.post('/place/', json.dumps(data), content_type='application/json')

        self.assertEquals(response.json(), {"message": "PLACE_CREATED"})
        self.assertEquals(response.status_code, 201)


class readTest(TestCase):
    def setUp(self):
        test_metro = MetroRegion.objects.create(name='테스트광역시')
        test_local = LocalRegion.objects.create(name='테스트구', metro_region=test_metro)
        test_type  = PlaceType.objects.create(name='테스트타입')
        test_place = Place.objects.create(id = 1, place_type = test_type, region = test_local, road_address = '테스트로 1', name = '테스트')
        test_place_2 = Place.objects.create(id = 2, place_type = test_type, region = test_local, road_address = '테스트로 1', name = '테스트2', deleted_at = timezone.now())


    def tearDown(self):
        MetroRegion.objects.all().delete()
        LocalRegion.objects.all().delete()
        PlaceType.objects.all().delete()
        Place.objects.all().delete()

    def test_read(self):
        client = Client()

        response = client.get('/place/1', content_type = 'application/json')

        self.assertEquals(response.json(), {"place": {"id": 1, "name": "테스트", "type": "테스트타입", "road_address": "테스트로 1", "local_region": "테스트구", "metro_region": "테스트광역시"}})
        self.assertEquals(response.status_code, 200)

    def test_deleted_place_read(self):
        client = Client()

        response = client.get('/place/2', content_type = 'application/json')

        self.assertEquals(response.json(), {"message": "DELETED_PLACE"})
        self.assertEquals(response.status_code, 401)

    def test_deleted_place_read(self):
        client = Client()

        response = client.get('/place/99', content_type = 'application/json')

        self.assertEquals(response.json(), {"message": "INVALID_PLACE_ID"})
        self.assertEquals(response.status_code, 401)


class updateTest(TestCase):
    def setUp(self):
        test_metro = MetroRegion.objects.create(name='테스트광역시')
        test_local = LocalRegion.objects.create(name='테스트구', metro_region=test_metro)
        test_type  = PlaceType.objects.create(name='테스트타입')
        test_place = Place.objects.create(id = 1, place_type = test_type, region = test_local, road_address = '테스트로 1', name = '테스트')
        test_place_2 = Place.objects.create(id = 2, place_type = test_type, region = test_local, road_address = '테스트로 1', name = '테스트2', deleted_at = timezone.now())


    def tearDown(self):
        MetroRegion.objects.all().delete()
        LocalRegion.objects.all().delete()
        PlaceType.objects.all().delete()
        Place.objects.all().delete()

    def test_update(self):
        client = Client()
        data = {
                'place_type'   : '테스트타입',
                'metro_region' : '테스트광역시',
                'local_region' : '테스트구',
                'road_address' : '수정테스트로 1',
                'name'         : '수정테스트'
                }

        response = client.patch('/place/1', json.dumps(data), content_type='application/json')

        self.assertEquals(response.json(), {"message": "PLACE_UPDATED"})
        self.assertEquals(response.status_code, 200)

        self.assertEquals(Place.objects.get(id=1).road_address, '수정테스트로 1')
        self.assertEquals(Place.objects.get(id=1).name, '수정테스트')

    def test_address_format(self):
        client = Client()
        data = {
                'place_type'   : '테스트타입',
                'metro_region' : '테스트광역시',
                'local_region' : '테스트구',
                'road_address' : '수정테스트',
                'name'         : '수정테스트'
                }

        response = client.patch('/place/1', json.dumps(data), content_type='application/json')

        self.assertEquals(response.json(), {"message": "INVALID_ROAD_ADDRESS_FORMAT"})
        self.assertEquals(response.status_code, 400)

    def test_deleted_place_update(self):
        client = Client()
        data = {
                'place_type'   : '테스트타입',
                'metro_region' : '테스트광역시',
                'local_region' : '테스트구',
                'road_address' : '수정테스트로 1',
                'name'         : '수정테스트'
                }

        response = client.patch('/place/2', json.dumps(data), content_type='application/json')

        self.assertEquals(response.json(), {"message": "DELETED_PLACE"})
        self.assertEquals(response.status_code, 400)


class deleteTest(TestCase):
    def setUp(self):
        test_metro = MetroRegion.objects.create(name='테스트광역시')
        test_local = LocalRegion.objects.create(name='테스트구', metro_region=test_metro)
        test_type  = PlaceType.objects.create(name='테스트타입')
        test_place = Place.objects.create(id = 1, place_type = test_type, region = test_local, road_address = '테스트로 1', name = '테스트')
        test_place_2 = Place.objects.create(id = 2, place_type = test_type, region = test_local, road_address = '테스트로 1', name = '테스트2', deleted_at = timezone.now())


    def tearDown(self):
        MetroRegion.objects.all().delete()
        LocalRegion.objects.all().delete()
        PlaceType.objects.all().delete()
        Place.objects.all().delete()

    def test_delete(self):
        client = Client()

        response = client.delete('/place/1', content_type='application/json')

        self.assertEquals(response.json(), {"message": "PLACE_DELETED"})
        self.assertEquals(response.status_code, 200)

        self.assertEquals(str(type(Place.objects.get(id=1).deleted_at)), "<class 'datetime.datetime'>")

    def test_deleted_place_delete(self):
        client = Client()

        response = client.delete('/place/2', content_type='application/json')

        self.assertEquals(response.json(), {"message": "PLACE_IS_ALREADY_DELETED"})
        self.assertEquals(response.status_code, 400)

    def test_invalid_place_delete(self):
        client = Client()

        response = client.delete('/place/99', content_type='application/json')

        self.assertEquals(response.json(), {"message": "INVALID_PLACE"})
        self.assertEquals(response.status_code, 401)


