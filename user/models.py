from django.db import models

class User(models.Model):
    """유저 테이블"""
    email      = models.EmailField()
    password   = models.CharField(max_length = 150)
    nickname   = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.nickname
