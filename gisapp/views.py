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
            # Парсим JSON данные
            data = json.loads(request.body)
            bbox = data.get('bbox')
            
            # Проверка наличия и формата bbox
            if not bbox or len(bbox) != 4:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Неверный формат bbox. Ожидается массив [west, south, east, north]'
                })
            
            # Проверка типа данных
            try:
                west = float(bbox[0])
                south = float(bbox[1])
                east = float(bbox[2])
                north = float(bbox[3])
            except (TypeError, ValueError) as e:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Ошибка преобразования координат: {str(e)}. Полученные значения: {bbox}'
                })
            
            # Проверка валидности координат
            if west >= east or south >= north:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Некорректные значения координат: west={west}, south={south}, east={east}, north={north}'
                })
            
            # Проверка размера области (не более 0.25 кв. градусов)
            area = (east - west) * (north - south)
            if area > 0.25:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Область слишком большая ({area:.4f} кв. градусов). Максимальный размер: 0.25 кв. градусов.'
                })
            
            # Создаем запрос к Overpass API
            overpass_query = f"""
                [out:xml][timeout:180];
                (
                    node({south}, {west}, {north}, {east});
                    way({south}, {west}, {north}, {east});
                    relation({south}, {west}, {north}, {east});
                );
                (._;>;);
                out body;
            """
            
            # Отправляем запрос к Overpass API
            try:
                response = requests.post(
                    'https://overpass-api.de/api/interpreter',
                    data=overpass_query,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    timeout=300  # 5 минут таймаут
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Ошибка при запросе к Overpass API: {str(e)}'
                })
            
            # Создаем временный файл для данных OSM
            try:
                with tempfile.NamedTemporaryFile(suffix='.osm', delete=False) as tmpfile:
                    tmpfile.write(response.content)
                    osm_file_path = tmpfile.name
            except IOError as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Ошибка создания временного файла: {str(e)}'
                })
            
            # Получаем параметры подключения к БД
            db_config = settings.DATABASES['default']
            
            # Формируем команду для osm2pgsql
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
            
            # Устанавливаем переменные окружения
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['PASSWORD']
            
            # Выполняем команду osm2pgsql
            try:
                result = subprocess.run(
                    cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 минут таймаут
                )
                
                if result.returncode != 0:
                    # Формируем сообщение об ошибке
                    error_msg = f"Ошибка osm2pgsql (код {result.returncode}): "
                    if result.stderr:
                        error_msg += result.stderr[:500]  # Берем первые 500 символов ошибки
                    else:
                        error_msg += "Без сообщения об ошибке"
                    
                    return JsonResponse({
                        'status': 'error',
                        'message': error_msg
                    })
            except subprocess.TimeoutExpired:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Превышено время выполнения osm2pgsql (10 минут)'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Ошибка выполнения osm2pgsql: {str(e)}'
                })
            finally:
                # Удаляем временный файл в любом случае
                try:
                    os.unlink(osm_file_path)
                except OSError:
                    pass
            
            # Проверяем, что данные действительно загружены
            try:
                with connection.cursor() as cursor:
                    # Проверяем наличие точек
                    cursor.execute("SELECT COUNT(*) FROM planet_osm_point")
                    point_count = cursor.fetchone()[0]
                    
                    # Проверяем наличие линий
                    cursor.execute("SELECT COUNT(*) FROM planet_osm_line")
                    line_count = cursor.fetchone()[0]
                    
                    # Проверяем наличие полигонов
                    cursor.execute("SELECT COUNT(*) FROM planet_osm_polygon")
                    polygon_count = cursor.fetchone()[0]
                    
                    total_count = point_count + line_count + polygon_count
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Данные загружены, но возникла ошибка при проверке: {str(e)}'
                })
            
            if total_count == 0:
                return JsonResponse({
                    'status': 'warning',
                    'message': 'Данные загружены, но не найдено объектов OSM в указанной области'
                })
            
            return JsonResponse({
                'status': 'success',
                'message': f'Данные OSM успешно загружены! Объектов: точек={point_count}, линий={line_count}, полигонов={polygon_count}'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Неверный формат JSON в теле запроса'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Необработанная ошибка: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Неверный метод запроса. Используйте POST.'
    })