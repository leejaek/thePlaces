from django.db import models

class MetroRegion(models.Model):
    """광역 지역 (특별시, 광역시, 도, 특별자치시, 특별자치도)"""
    name = models.CharField(max_length=20, unique = True)

    class Meta:
        db_table = 'metro_regions'

class LocalRegion(models.Model):
    """지역 (시, 구, 읍, 면, 동)"""
    name         = models.CharField(max_length=20)
    metro_region = models.ForeignKey(MetroRegion, on_delete=models.CASCADE)

    class Meta:
        db_table = 'local_regions'

class PlaceType(models.Model):
    """장소 유형"""
    name = models.CharField(max_length=20, unique = True)

    class Meta:
        db_table = 'place_types'


class Place(models.Model):
    """장소 테이블"""
    name = models.CharField(max_length=50)
    place_type   = models.ForeignKey(PlaceType, on_delete = models.CASCADE)
    region       = models.ForeignKey(LocalRegion, on_delete = models.CASCADE)
    road_address = models.CharField(max_length=50)
    created_at   = models.DateTimeField(auto_now_add = True)
    updated_at   = models.DateTimeField(auto_now = True)
    deleted_at   = models.DateTimeField(null = True)

    class Meta:
        db_table = 'places'
