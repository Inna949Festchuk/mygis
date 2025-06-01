from django.urls import path
from .views import get_context_data
from .views import clear_database
from . import consumers

app_name = 'gisapp'

urlpatterns = [
    path('map/', get_context_data, name='add_map'),
    path('clear-db/', clear_database, name='clear_db')
    # path('ws/index/', consumers.IndexConsumer.as_asgi()),
]

