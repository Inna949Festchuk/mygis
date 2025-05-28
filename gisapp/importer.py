import os
import logging
import pathlib
import time
import threading
from django.conf import settings
from django.contrib.gis.geos import MultiPoint, Point
from .models import ValuesPoints
from .tasks import save_data_to_database


logger = logging.getLogger(__name__)

class DataImporter:
    """
    Класс для импорта данных из текстовых файлов в определённой директории, 
    парсинга и обработки этих данных, а также сохранения их в базе данных.
    """
    def __init__(self):
        self.data_dir = pathlib.Path(settings.BASE_DIR) / 'gisapp' / 'indata'
        self.processed_dir = self.data_dir / 'processed'
        self.processed_dir.mkdir(exist_ok=True)

    def start(self):
        """
        Запускает процесс импорта данных в отдельном потоке,
        чтобы импорт не мешал выполнению основной программы.
        """
        thread = threading.Thread(target=self.run_import)
        thread.daemon = True
        thread.start()

    def run_import(self):
        """
        Запускает процесс импорта данных в бесконечном цикле, 
        проверяя наличие новых файлов каждые 60 секунд в директории
        `self.data_dir`.
        """
        while True:
            self.check_files() # проверяем наличие новых файлов
            time.sleep(60)

    def check_files(self):
        """
        Проверяет наличие новых файлов .txt в директории `self.data_dir` 
        и обрабатывает каждый новый файл.
        """
        try:
            for filename in self.data_dir.iterdir():
                if filename.suffix == '.txt':
                    self.process_file(filename)
        except Exception as e:
            logger.error(f"Error checking files: {str(e)}")

    def process_file(self, filepath):
        """
        Обрабатывает текстовый файл `filepath`, парся его содержимое, 
        создавая объекты базы данных, исключая их дублирование, и сохраняя их в базу данных. 
        Также перемещает обработанный файл в отдельную директорию.
        """
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()

            records = []
            for line in lines[1:]:
                fields = [f.strip() for f in line.strip().split(',') if f.strip()]

                if len(fields) < 11:
                    continue

                try:
                    # Парсинг данных
                    latitude = float(fields[2])
                    if fields[3] == 'S':
                        latitude = -latitude

                    longitude = float(fields[4])
                    if fields[5] == 'W':
                        longitude = -longitude
                        
                    # Сохранение данных в базу данных с проверкой на уникальность
                    obj, created = ValuesPoints.objects.get_or_create(utc_time=float(fields[0]), state=fields[1], latitude=latitude, longitude=longitude,
                        defaults={
                            'n_s_indica': fields[3],
                            'e_w_indica': fields[5],
                            'ground_spe': float(fields[6]),
                            'position': float(fields[7]),
                            'date': float(fields[8]),
                            'f2': float(fields[9]),
                            'f3': float(fields[10]),
                            'geom': MultiPoint(Point(longitude, latitude))
                        })
                    if created:
                        records.append(obj)

                except Exception as e:
                    logger.error(f"Error parsing data in file {filepath}: {str(e)}")

            # Массовое сохранение
            try:
                save_data_to_database(records)
            except Exception as e:
                logger.error(f"Error saving data to database: {str(e)}")

            # Перемещение обработанного файла
            try:
                processed_path = self.processed_dir / f"{filepath.name}_{int(time.time())}"
                filepath.replace(processed_path)
            except Exception as e:
                logger.error(f"Error moving file {filepath}: {str(e)}")

        except Exception as e:
            logger.error(f"Error processing file {filepath}: {str(e)}")
