import os
import time
import threading # для потоков
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
        importer = DataImporter()
        # Start the DataImporter thread
        importer.start()
