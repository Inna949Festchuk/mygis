from django.urls import path
from .views import get_context_data
from .views import clear_database
from .views import get_csrf_token
from . import consumers

app_name = 'gisapp'

urlpatterns = [
    path('map/', get_context_data, name='add_map'),
    path('clear-db/', clear_database, name='clear_db'),
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    # path('ws/index/', consumers.IndexConsumer.as_asgi()),
]

