# Импорт shape в gdb с помощью LayerMapping
from pathlib import Path
from django.contrib.gis.utils import LayerMapping
from .models import ValuesPoints

# Все это дело можно автоматизировать
# введя в bash
# python manage.py ogrinspect gisapp/indata/Points.shp ValuesPoints --srid=4326 --mapping --multi
# тогда на выходе мы получим модель

# class ValuesPoints(models.Model):
#     utc_time = models.FloatField()
#     state = models.CharField(max_length=254)
#     latitude = models.FloatField()
#     n_s_indica = models.CharField(max_length=254)
#     longitude = models.FloatField()
#     e_w_indica = models.CharField(max_length=254)
#     ground_spe = models.FloatField()
#     position = models.FloatField()
#     date = models.FloatField()
#     f2 = models.FloatField()
#     f3 = models.FloatField()
#     f12 = models.CharField(max_length=254)
#     geom = models.MultiPointField(srid=4326)


valuespoints_mapping = {
    'utc_time': 'UTC_time',
    'state': 'state',
    'latitude': 'latitude',
    'n_s_indica': 'N_S_Indica',
    'longitude': 'longitude',
    'e_w_indica': 'E_W_indica',
    'ground_spe': 'Ground_spe',
    'position': 'position',
    'date': 'date',
    'f2': 'f2',
    'f3': 'f3',
    'f12': 'F12',
    'geom': 'MULTIPOINT',
}

valuespoints_mapping_shp = Path(__file__).resolve().parent / "indata" / "points.shp"

def run(verbose=True):
    lm = LayerMapping(ValuesPoints, valuespoints_mapping_shp, valuespoints_mapping, transform=True) # преобразуем в заданную в моделе СК (при необходимости)
    lm.save(strict=True, verbose=verbose)


# После этого вызовите оболочку Django из каталога проекта geodjango
# python manage.py shell
# Далее импортируем модуль load, вызываем процедуру run и наблюдаем, 
# как LayerMapping выполняет свою работу
# from gisapp import load
# load.run()