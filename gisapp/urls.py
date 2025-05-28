from django.urls import path
from .views import get_context_data
from . import consumers

app_name = 'gisapp'

urlpatterns = [
    path('map/', get_context_data),
    # path('ws/index/', consumers.IndexConsumer.as_asgi()),
]

