import tempfile
import requests

def get_osm_data(bbox_polygon):
    """
    Скачивает данные OSM для заданного полигона
    Возвращает временный файл с данными в формате PBF
    """
    # Форматируем bbox для Overpass API
    min_lon, min_lat, max_lon, max_lat = bbox_polygon.extent
    bbox_str = f'{min_lat},{min_lon},{max_lat},{max_lon}'
    
    # Создаем запрос к Overpass API
    overpass_query = f"""
        [out:xml][timeout:180];
        (
            node[{bbox_str}];
            way[{bbox_str}];
            relation[{bbox_str}];
        );
        (._;>;);
        out body;
    """
    
    # Скачиваем данные
    response = requests.post(
        'https://overpass-api.de/api/interpreter',
        data=overpass_query,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    response.raise_for_status()
    
    # Сохраняем во временный файл
    osm_file = tempfile.NamedTemporaryFile(suffix='.osm', delete=False)
    osm_file.write(response.content)
    osm_file.flush()
    
    return osm_file