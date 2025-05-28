from django.shortcuts import render
from django.core.serializers import serialize
import json
from .models import ValuesPoints
import logging

logger = logging.getLogger(__name__)

def get_context_data(request):
    try:
        data_geojson = serialize('geojson', ValuesPoints.objects.all(), geometry_field='geom', fields=('f3',))
        context = {
            'context': json.loads(data_geojson),
        }
        return render(request, 'index.html', context)
    except Exception as e:
        logger.error(f"Error getting context data: {str(e)}")
        return render(request, 'error.html')


