import os
import time
import threading
from django.apps import AppConfig


class GisappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gisapp'

    def ready(self):
        """
        Функция вызывается, когда приложение готово к запуску. 
        Здесь мы запускаем поток DataImporter.
        """
        from .models import ValuesPoints
        from .importer import DataImporter
        # Create an instance of the DataImporter class
        importer = DataImporter()
        # Start the DataImporter thread
        importer.start()
