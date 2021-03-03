from django.db import models

from place.models import Place
from user.models  import User

class CheckIn(models.Model):
    user       = models.ForeignKey('user.User', on_delete=models.CASCADE)
    place      = models.ForeignKey('place.Place', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'checkins'


class Review(models.Model):
    user       = models.ForeignKey('user.User', on_delete=models.CASCADE)
    place      = models.ForeignKey('place.Place', on_delete=models.CASCADE)
    body       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'reviews'

