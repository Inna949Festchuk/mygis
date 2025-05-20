from django.urls import path
from .views import get_context_data

app_name = 'gisapp'

urlpatterns = [
    path('map/', get_context_data),
]