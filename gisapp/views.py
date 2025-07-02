import json
import logging
import time
from django.conf import settings
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from .models import ValuesPoints
from django.http import JsonResponse

import requests
import os
import subprocess
import tempfile
from django.contrib.gis.geos import Polygon
from gisapp.utils import get_osm_data  


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
        """
        Поток событий
        """
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


 
# @csrf_exempt
# def load_osm(request):
#     if request.method == 'POST':
#         try:
#             # Получаем bbox из запроса
#             bbox_str = request.POST.get('bbox', '')
#             bbox = [float(coord) for coord in bbox_str.split(',')]
            
#             if len(bbox) != 4:
#                 return JsonResponse({'status': 'error', 'message': 'Invalid bbox format'})
            
#             # Форматируем bbox для Overpass API (south, west, north, east)
#             south, west, north, east = bbox[1], bbox[0], bbox[3], bbox[2]
            
#             # Создаем корректный запрос к Overpass API
#             overpass_query = f"""
#                 [out:xml][timeout:180];
#                 (
#                     node({south}, {west}, {north}, {east});
#                     way({south}, {west}, {north}, {east});
#                     relation({south}, {west}, {north}, {east});
#                 );
#                 (._;>;);
#                 out body;
#             """
            
#             # Отправляем запрос к Overpass API
#             response = requests.post(
#                 'https://overpass-api.de/api/interpreter',
#                 data=overpass_query,
#                 headers={'Content-Type': 'application/x-www-form-urlencoded'}
#             )
#             response.raise_for_status()
            
#             # Сохраняем ответ во временный файл
#             with tempfile.NamedTemporaryFile(suffix='.osm', delete=False) as tmpfile:
#                 tmpfile.write(response.content)
#                 osm_file_path = tmpfile.name
            
#             # Параметры подключения к БД
#             db_config = settings.DATABASES['default']
#             cmd = [
#                 'osm2pgsql',
#                 '--create',
#                 '--slim',
#                 '--hstore',
#                 '--prefix', 'planet_osm',
#                 '--proj', '3857',
#                 '--database', db_config['NAME'],
#                 '--username', db_config['USER'],
#                 '--host', db_config['HOST'] or 'localhost',
#                 '--port', db_config['PORT'] or '5432',
#                 osm_file_path
#             ]
            
#             env = os.environ.copy()
#             env['PGPASSWORD'] = db_config['PASSWORD']
            
#             # Запускаем процесс
#             result = subprocess.run(
#                 cmd,
#                 env=env,
#                 capture_output=True,
#                 text=True
#             )
            
#             # Удаляем временный файл
#             os.unlink(osm_file_path)
            
#             if result.returncode == 0:
#                 return JsonResponse({'status': 'success', 'message': 'Данные успешно загружены в PostGIS'})
#             else:
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': f'Ошибка загрузки: {result.stderr}'
#                 })
                
#         except Exception as e:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': f'Системная ошибка: {str(e)}'
#             })
#     return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'})


import os
import json
import tempfile
import subprocess
import requests
import shutil
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import connection
from django.contrib.gis.geos import Polygon

@csrf_exempt
def load_osm(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bbox = data.get('bbox')
            
            # Валидация bbox
            if not bbox or len(bbox) != 4:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Неверный формат bbox'
                })
            
            # Создаем полигон для проверки
            poly = Polygon.from_bbox(bbox)
            if poly.area > 0.25:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Область слишком большая'
                })
            
            # Формируем запрос к Overpass API
            overpass_query = f"""
                [out:xml][timeout:180];
                (
                    node({bbox[1]}, {bbox[0]}, {bbox[3]}, {bbox[2]});
                    way({bbox[1]}, {bbox[0]}, {bbox[3]}, {bbox[2]});
                    relation({bbox[1]}, {bbox[0]}, {bbox[3]}, {bbox[2]});
                );
                (._;>;);
                out body;
            """
            
            # Отправка запроса
            response = requests.post(
                'https://overpass-api.de/api/interpreter',
                data=overpass_query,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=300
            )
            response.raise_for_status()
            
            # Сохранение во временный файл
            with tempfile.NamedTemporaryFile(suffix='.osm', delete=False) as tmpfile:
                tmpfile.write(response.content)
                osm_file_path = tmpfile.name
            
            # Загрузка в PostGIS
            db_config = settings.DATABASES['default']
            cmd = [
                'osm2pgsql',
                '--create',
                '--slim',
                '--hstore',
                '--prefix', 'planet_osm',
                '--proj', '3857',
                '--database', db_config['NAME'],
                '--username', db_config['USER'],
                '--host', db_config['HOST'],
                '--port', db_config['PORT'],
                osm_file_path
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['PASSWORD']
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            # Удаление временного файла
            os.unlink(osm_file_path)
            
            if result.returncode != 0:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Ошибка osm2pgsql: {result.stderr[:500]}'
                })
            
            return JsonResponse({
                'status': 'success',
                'message': 'Данные OSM успешно загружены'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Ошибка: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Неверный метод запроса'
    })