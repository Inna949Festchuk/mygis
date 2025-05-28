from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpRequest
# from .views import get_context_data
from django.template.loader import get_template
from django.template import Context

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



# @receiver(post_save, sender=ValuesPoints)
# def update_context(sender, instance, created, **kwargs):
#     if created:
#         request = HttpRequest()
#         request.method = 'GET'
#         context = get_context_data(request)
#         template = get_template('index.html')
#         context = Context(context)
#         html = template.render(context)
#         # сохранить html в файл или отправить его клиенту
#         return HttpResponse(html)
        
