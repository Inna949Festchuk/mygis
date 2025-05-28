
from .models import ValuesPoints
from .views import get_context_data

def save_data_to_database(records):
    ValuesPoints.objects.bulk_create(records)
    get_context_data(request) # вызов функции get_context_data
   