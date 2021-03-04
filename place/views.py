import json
import re

from django.http import JsonResponse
from django.views import View
from django.utils import timezone

from .models import MetroRegion, LocalRegion, PlaceType, Place

REGEX_ROAD_ADDRESS = '(([가-힣A-Za-z·\d~\-\.]{2,}(로|길).[\d]+)|([가-힣A-Za-z·\d~\-\.]+(읍|동)\s)[\d]+)'

class PlaceCreateView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            place_type = PlaceType.objects.get(name = data['place_type'])
            metro_region = MetroRegion.objects.get(name=data['metro_region'])
            local_region = LocalRegion.objects.get(name=data['local_region'], metro_region = metro_region)
            road_address = data['road_address']
            name = data['name']
            
            assert re.match(REGEX_ROAD_ADDRESS, road_address), "INVALID_ROAD_ADDRESS_FORMAT"

            if Place.objects.filter(name = name, place_type = place_type, road_address = road_address, region = local_region, deleted_at = None).exists():
                return JsonResponse({"message": "EXIST_PLACE"}, status = 400)
            
            Place.objects.create(
                    name         = name,
                    place_type   = place_type,
                    road_address = road_address,
                    region       = local_region
            )
            return JsonResponse({"message": "PLACE_CREATED"}, status = 201)
        
        except json.JSONDecodeError as e:
            return JsonResponse({"message": f"{e}"}, status = 400)
        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status = 400)
        except AssertionError as e:
            return JsonResponse({"message": f"{e}"}, status = 400)
        except PlaceType.DoesNotExist:
            return JsonResponse({"message": "INVALID_PLACE_TYPE"}, status = 401)
        except MetroRegion.DoesNotExist:
            return JsonResponse({"message": "INVALID_REGION"}, status = 401)
        except LocalRegion.DoesNotExist:
            return JsonResponse({"message": "INVALID_REGION"}, status = 401)
    
    def get(self, request):
        places = Place.objects.select_related('place_type', 'region', 'region__metro_region').filter(deleted_at__isnull = True)

        result = [
                    {
                        "id"           : place.id,
                        "name"         : place.name,
                        "type"         : place.place_type.name,
                        "road_address" : place.road_address,
                        "local_region" : place.region.name,
                        "metro_region" : place.region.metro_region.name
                    } for place in places
                ]
        return JsonResponse({"result": result}, status = 200)



class PlaceView(View):
    def patch(self, request, place_pk):
        try:
            data = json.loads(request.body)
            
            data_keys = data.keys()
            
            place_type = PlaceType.objects.get(name = data['place_type'])
            metro_region = MetroRegion.objects.get(name=data['metro_region'])
            local_region = LocalRegion.objects.get(name=data['local_region'], metro_region = metro_region)
            road_address = data['road_address']
            name = data['name']

            assert re.match(REGEX_ROAD_ADDRESS, road_address), "INVALID_ROAD_ADDRESS_FORMAT"

            patch_object = Place.objects.get(id = place_pk)

            if patch_object.deleted_at == None:
                patch_object.place_type   = place_type
                patch_object.region       = local_region
                patch_object.road_address = road_address
                patch_object.name         = name
                patch_object.save()
                return JsonResponse({"message": "PLACE_UPDATED"}, status = 200)
            else:
                return JsonResponse({"message": "DELETED_PLACE"}, status = 400)

        except json.JSONDecodeError as e:
            return JsonResponse({"message": f"{e}"}, status = 400)
        except AssertionError as e:
            return JsonResponse({"message": f"{e}"}, status = 400)
        except Place.DoesNotExist:
            return JsonResponse({"message": "INVALID_PLACE"}, status = 401)
        except PlaceType.DoesNotExist:
            return JsonResponse({"message": "INVALID_PLACE_TYPE"}, status = 401)
        except MetroRegion.DoesNotExist:
            return JsonResponse({"message": "INVALID_REGION"}, status = 401)
        except LocalRegion.DoesNotExist:
            return JsonResponse({"message": "INVALID_REGION"}, status = 401)

    def delete(self, request, place_pk):
        try:
            delete_object = Place.objects.get(id = place_pk)
            
            if delete_object.deleted_at == None:
                delete_object.deleted_at = timezone.now()
                delete_object.save()
                return JsonResponse({"message": "PLACE_DELETED"}, status = 200)
            else:
                return JsonResponse({"message": "PLACE_IS_ALREADY_DELETED"}, status = 400)
        except Place.DoesNotExist:
            return JsonResponse({"message": "INVALID_PLACE"}, status = 401)
