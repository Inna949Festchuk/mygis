from django.urls import path
from .views import get_context_data
from .views import clear_database
from .views import get_csrf_token
from .views import get_geojson_data
from .views import data_updates
from .views import load_my_osm

app_name = 'gisapp'

urlpatterns = [
    path('map/', get_context_data, name='add_map'),
    path('clear-db/', clear_database, name='clear_db'),
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('geojson-data/', get_geojson_data, name='geojson_data'),
    path('data-updates/', data_updates, name='data_updates'),
    path('load_osm/', load_my_osm, name='load_my_osm'),
]

