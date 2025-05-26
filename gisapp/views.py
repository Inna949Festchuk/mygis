import json 

from django.shortcuts import render
from .models import ValuesPoints
from django.core.serializers import serialize


def get_context_data(request):
    data_geojson = serialize('geojson', ValuesPoints.objects.all(),
            geometry_field='geom',
            fields=('f3',)) # поле по которому производится построение тепловой карты (на фронте)
    
    valid_data = json.loads(data_geojson)
    
    context = {
        'context': valid_data,
        }

    return render(request, 'index.html', context)