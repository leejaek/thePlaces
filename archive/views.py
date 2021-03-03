import json

from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from django.db.models import Count

from .models import CheckIn, Review
from user.models import User
from place.models import Place

from user.utils import id_auth

class CheckInView(View):
    @id_auth
    def post(self, request, place_pk):
        try:
            user = request.user
            
            if CheckIn.objects.filter(user = user, place_id = place_pk, deleted_at__isnull = True).exists():
                recent_checkin = CheckIn.objects.filter(user = user, place_id = place_pk, deleted_at__isnull = True).latest('created_at')
                if (timezone.now() - recent_checkin.created_at).days == 0:
                    return JsonResponse({"message": "ALREADY_CHECKED_IN_TODAY"}, status = 401)
            
            CheckIn.objects.create(user = user, place_id = place_pk)
            return JsonResponse({"message": "CHECKED_IN"}, status = 201)

        except Place.DoesNotExist:
            return JsonResponse({"message": "INVALID_PLACE"}, status = 401)
        
    @id_auth
    def get(self, request, place_pk):
        user = request.user
        checkins = CheckIn.objects.filter(user = user, place_id = place_pk, deleted_at__isnull = True)

        result = [
                    {
                        "id": checkin.id,
                        "created_at": checkin.created_at.strftime('%Y-%m-%d')
                    } for checkin in checkins
                ]
        return JsonResponse({"result": result}, status = 200)


class CheckInDeleteView(View):
    @id_auth
    def delete(self, request, checkin_pk):
        try:
            user = request.user
            delete_object = CheckIn.objects.get(id = checkin_pk, deleted_at__isnull = True)

            if delete_object.user == user:
                delete_object.deleted_at = timezone.now()
                delete_object.save()
                return JsonResponse({"message": "DELETED"}, status = 204)
            else:
                return JsonResponse({"message": "UNAUTHORIZED"}, status = 401)

        except CheckIn.DoesNotExist:
            return JsonResponse({"message": "INVALID_CHECKIN"}, status = 400)


