# from django.db import models
from django.contrib.gis.db import models

class ExitBorder(models.Model):
    objectid = models.IntegerField()
    values = models.FloatField()
    geom = models.PointField(srid=4326)
