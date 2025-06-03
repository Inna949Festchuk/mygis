import json
import logging
import time
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from .models import ValuesPoints
from django.http import JsonResponse


logger = logging.getLogger(__name__)

def get_context_data(request):
    """
    Функция для получения контекстных данных из БД и передачи их в шаблон.
    """
    try:
        data_geojson = serialize('geojson', ValuesPoints.objects.all(), geometry_field='geom', fields=('f3',))
        context = {
            'context': json.loads(data_geojson),
        }
        return render(request, 'index.html', context)
    except Exception as e:
        logger.error(f"Error getting context data: {str(e)}")
        return render(request, 'error.html')


def get_geojson_data(request):
    """
    Функция для получения данных в формате GeoJSON
    """
    try:
        data_geojson = serialize('geojson', ValuesPoints.objects.all(), geometry_field='geom', fields=('f3',))
        return JsonResponse(json.loads(data_geojson), safe=False)
    except Exception as e:
        logger.error(f"Error getting GeoJSON data: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt # декоратор для отключения проверки CSRF-токена
def clear_database(request):
    """
    Функция для очистки базы данных.
    """
    if request.method == 'POST':
        try:
            ValuesPoints.objects.all().delete()
            logger.info("Database cleared successfully")
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def get_csrf_token(request):
    """
    Функция для получения CSRF-токена.
    """
    return JsonResponse({'csrfToken': get_token(request)})


def data_updates(request):
    """Потоковое обновление данных через Server-Sent Events"""
    def event_stream():
        last_count = ValuesPoints.objects.count() # получаем предыдущее количество объектов
        while True:
            time.sleep(1)  # Проверяем каждую секунду
            current_count = ValuesPoints.objects.count()
            
            # Если количество объектов изменилось
            if current_count != last_count:
                last_count = current_count
                yield f"data: {json.dumps({'count': current_count})}\n\n" # отправляем событие - изменение количества объектов
    
    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache' # отключаем кэширование
    return response