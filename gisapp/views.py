from django.shortcuts import render
from django.core.serializers import serialize
import json
from .models import ValuesPoints
from django.http import JsonResponse
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


def clear_database(request):
    if request.method == 'POST':
        try:
            # Очищаем базу данных
            ValuesPoints.objects.all().delete()
            logger.info("Database cleared successfully")
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
