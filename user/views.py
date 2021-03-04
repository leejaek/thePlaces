import json
import re

from datetime import timedelta

from django.http  import JsonResponse
from django.views import View
from django.utils import timezone

import jwt
import bcrypt

from .models import User
from local_settings import SECRET_KEY, ALGORITHM

REGEX_EMAIL = '([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,4}))'
REGEX_PASSWORD = '^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}$'


class SignUpView(View):
    def post(self, request):
        try:
            data     = json.loads(request.body)
            nickname = data['nickname']
            email    = data['email']
            password = data['password']

            assert re.match(REGEX_EMAIL, email), "INVALID_EMAIL_FORMAT"
            assert re.match(REGEX_PASSWORD, password), "INVALID_PASSWORD_FORMAT"

            assert not User.objects.filter(email=email), "ALREADY_EXISTS_ACCOUNT"
            assert not User.objects.filter(nickname = nickname), "ALREADY_EXISTS_NICKNAME"

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

            User.objects.create(
                    email = email,
                    password = hashed_password,
                    nickname = nickname,
            )

            return JsonResponse({"message": "SUCCESS"}, status = 201)

        except json.JSONDecodeError as e:
            return JsonResponse({"message": f"{e}"}, status = 400)
        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status = 400)
        except AssertionError as e:
            return JsonResponse({"message": f"{e}"}, status = 400)

class SignInView(View):
    def post(self, request):
        try:
            data        = json.loads(request.body)
            email       = data['email']
            password    = data['password']
            signin_user = User.objects.get(email = email)

            if bcrypt.checkpw(password.encode('utf-8'), signin_user.password.encode('utf-8')):
                access_token = jwt.encode({'id': signin_user.id, 'exp': timezone.localtime() + timedelta(hours=24)}, SECRET_KEY, algorithm=ALGORITHM)
                access_token = jwt.encode({'id': signin_user.id}, SECRET_KEY, algorithm=ALGORITHM)
                

                return JsonResponse({"message": "SUCCESS", "access_token": access_token}, status = 200)
            else:
                return JsonResponse({"message": "INVALID_USER_EMAIL_OR_PASSWORD"}, status = 401)


        except json.JSONDecodeError as e:
            return JsonResponse({"message": f"{e}"}, status = 400)
        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status = 400)
        except User.DoesNotExist:
            return JsonResponse({"message": "INVALID_USER_EMAIL_OR_PASSWORD"}, status = 401)
