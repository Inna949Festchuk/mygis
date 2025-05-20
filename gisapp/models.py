from django.contrib.gis.db import models

class ValuesPoints(models.Model):
    utc_time = models.FloatField(null=True, blank=True)
    state = models.CharField(max_length=254, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    n_s_indica = models.CharField(max_length=254, null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    e_w_indica = models.CharField(max_length=254, null=True, blank=True)
    ground_spe = models.FloatField(null=True, blank=True)
    position = models.FloatField(null=True, blank=True)
    date = models.FloatField(null=True, blank=True)
    f2 = models.FloatField(null=True, blank=True)
    f3 = models.FloatField(null=True, blank=True)
    f12 = models.CharField(max_length=254, null=True, blank=True)
    geom = models.MultiPointField(srid=4326, null=True, blank=True) # WGS84=EPSG:4326, WebMercator=EPSG:3857
