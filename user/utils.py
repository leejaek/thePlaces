import jwt
import json
from functools import wraps

from django.utils import timezone
from django.http import JsonResponse

from user.models import User
from local_settings import SECRET_KEY, ALGORITHM

def id_auth(func):
    @wraps(func)
    def decorated_function(self, request, *args, **kwargs):
        try:
            access_token = request.headers.get('Authorization')
            payload      = jwt.decode(access_token, SECRET_KEY, algorithms=ALGORITHM)

            login_user   = User.objects.get(id = payload['id'])

            request.user = login_user
            return func(self, request, *args, **kwargs)
        
        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "EXPIRED_TOKEN"}, status = 400)
        except jwt.exceptions.DecodeError:
            return JsonResponse({"message": "INVALID_TOKEN"}, status = 400)
        except User.DoesNotExist:
            return JsonResponse({"message": "INVALID_USER"}, status = 400)
    return decorated_function

