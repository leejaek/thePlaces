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
            place = Place.objects.get(id = place_pk)

            if CheckIn.objects.filter(user = user, place = place, deleted_at__isnull = True).exists():
                recent_checkin = CheckIn.objects.filter(user = user, place = place, deleted_at__isnull = True).latest('created_at')
                if (timezone.now() - recent_checkin.created_at).days == 0:
                    return JsonResponse({"message": "ALREADY_CHECKED_IN_TODAY"}, status = 401)
            
            CheckIn.objects.create(user = user, place = place)
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
                return JsonResponse({"message": "CHECK_IN_DELETED"}, status = 204)
            else:
                return JsonResponse({"message": "UNAUTHORIZED"}, status = 401)

        except CheckIn.DoesNotExist:
            return JsonResponse({"message": "INVALID_CHECKIN"}, status = 400)

class ReviewView(View):
    @id_auth
    def post(self, request, place_pk):
        """해당 장소에 대한 리뷰 작성"""
        try:
            user = request.user
            place = Place.objects.get(id = place_pk)
            body = json.loads(request.body)['body']

            Review.objects.create(user = user, place= place, body = body)
            return JsonResponse({"message": "REVIEW_CREATED"}, status = 201)

        except json.JSONDecodeError as e:
            return JsonResponse({"message": f"{e}"}, status = 400)
        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status = 400)
        except Place.DoesNotExist:
            return JsonResponse({"message": "INVALID_PLACE"}, status = 400)

    def get(self, request, place_pk):
        """해당 장소에 대한 로그인 유저의 리뷰 조회"""
        try:
            place = Place.objects.get(id = place_pk)
            
            reviews = Review.objects.select_related('user').filter(place = place, deleted_at__isnull = True)

            result = [
                        {
                            "id": review.id,
                            "user": review.user.nickname, 
                            "body": review.body,
                            "created_at": review.created_at.strftime('%Y-%m-%d')
                        } for review in reviews
                    ]

            return JsonResponse({"result": result}, status = 200)
        except Place.DoesNotExist:
            return JsonResponse({"message": "INVALID_PLACE"}, status = 400)

class ReviewUpdateDeleteView(View):
    @id_auth
    def patch(self, request, review_pk):
        try:
            user   = request.user
            review = Review.objects.get(id = review_pk, deleted_at__isnull = True)
            body   = json.loads(request.body)['body']

            if review.user == user:
                review.body = body
                review.save()
                return JsonResponse({"message": "REVIEW_UPDATED"}, status = 200)
            else:
                return JsonResponse({"message": "UNAUTHORIZAED"}, status = 401)

        except json.JSONDecodeError as e:
            return JsonResponse({"message": f"{e}"}, status = 400)
        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status = 400)
        except Review.DoesNotExist:
            return JsonResponse({"message": "INVALID_REVIEW"}, status = 400)

    @id_auth
    def delete(self, request, review_pk):
        try:
            user   = request.user
            review = Review.objects.get(id = review_pk, deleted_at__isnull = True)
            
            if review.user == user:
                review.deleted_at = timezone.now()
                review.save()
                return JsonResponse({"message": "REVIEW_DELETED"}, status = 204)
            else:
                return JsonResponse({"message": "UNAUTHORIZED"}, status = 401)
        
        except Review.DoesNotExist:
            return JsonResponse({"message": "INVALID_REVIEW"}, status = 400)
