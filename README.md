![Пользовательский интерфейс](image.png)

# Настройки разработчика:

python3 -m venv venv

source venv/bin/activate

pip3 install django

pip3 freeze > requirements.txt

django-admin startproject gisproject .

python3 manage.py startapp gisapp

Установка OpenLayers offline

переходим по ссылкам 
https://cdn.jsdelivr.net/npm/ol@latest/dist/ol.js
https://cdn.jsdelivr.net/npm/ol@latest/ol.css

и сохраняем страницы в папки проекта, соответственно 
/gisapp
   /js
      ol.js
   /css
      ol.css
   index.html

В index.html меняем ссылки на оффлайн версию

<script src="{% static 'js/ol.js' %}"></script>
<link rel="stylesheet" href="{% static 'css/ol.css' %}">

Создаем тайловую оффлайн карту в QGIS (я использую расширение QTiles) и сохраняем в папку проекта tiles

![](download_tiles.png)

В index.html меняем ссылки на оффлайн версию

// source: new ol.source.OSM( )
на
source: new ol.source.XYZ({
   url: 'gisapp/static/tiles/{z}/{x}/{y}.png'
})

# РАЗВОРАЧИВАЕМ ПРИЛОЖЕНИЕ:

Создаем виртуальную среду, активируем ее и устанавливаем все зависимости
---
python3 -m venv venv

source venv/bin/activate

python3 -m pip install -r requirements.txt


# УСТАНАВЛИВАЕМ И НАСТРАИВАЕМ PostgreSQL+PostGIS

## На MacOS

- Установить PostgreSQL

- Проверить стартанула ли служба postgresql

- Задаем переменную среды PATH (если нужен не стандартный путь к утилитам postgresql (например на MACOS))
Так нужно делать при каждом новом запуске терминала 
PATH=$PATH:/Applications/Postgres.app/Contents/Versions/12/bin/

- Создаем БД с именем mygis
createdb -U postgres mygis

- Подключение к созданной БД
psql -U postgres -d mygis

- просмотр таблиц 
\d

- выход 
\q

- установка пароля зозданной БД
psql
ALTER USER postgres WITH PASSWORD 'mygispass';
Должны увидеть
ALTER ROLE
\q

- Устанавливаем расширение postgis
psql
CREATE EXTENSION postgis;
Должны увидеть CREATE EXTENSION
\q

## На Linux Manjaro

Переключаемся на пользователя
sudo su postgres

ALTER USER postgres WITH PASSWORD 'mygispass';

CREATE DATABASE mygis;

CREATE EXTENSION postgis;

\q
Переключаемся на юзера
exit

# ВНИМАНИЕ! 
### процедура загрузки данных из шейп-файла описана тут gisapp/load.py


# Установка приложения с помощью Docker-композа c Linux Ubuntu

1. Перед запуском команды остановите службу postgresql, если она запущена 
sudo systemctl stop postgresql 
sudo systemctl disable postgresql 
2. Запустите команду docker-compose up -d --build
3. Зайти в контейнер с помощью команды docker exec -it mygis-app-1 sh
4. Выполните команду python manage.py migrate
5. После этого вызовите оболочку Django из каталога проекта geodjango для загрузки данных из шейп-файла
python manage.py shell
6. Далее импортируем модуль load, вызываем процедуру run и наблюдаем, как LayerMapping выполняет свою работу
from gisapp import load
load.run()


# Развертывание Docker-проекта без интернета

Чтобы развернуть ваш Docker-проект без подключения к интернету, выполните следующие шаги:

### 1. Подготовка Docker образов на машине с интернетом
```bash
# Скачайте базовые образы
docker pull python:3.10-alpine
docker pull postgis/postgis:15-3.3

# Сохраните образы в архив
docker save -o python_image.tar python:3.10-alpine
docker save -o postgis_image.tar postgis/postgis:15-3.3
```

### 2. Подготовка APK пакетов
На машине с интернетом:
```bash
# Создайте директорию для пакетов
mkdir alpine-packages && cd alpine-packages

# Скачайте пакеты и их зависимости
apk fetch --no-cache gcc musl-dev gdal-dev geos-dev postgresql-client
```

Структура проекта после подготовки:
```
your-project/
├── alpine-packages/
│   ├── gcc-<version>.apk
│   ├── musl-dev-<version>.apk
│   └── ... 
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

### 3. Подготовка Python зависимостей
```bash
# Создайте директорию для пакетов Python
mkdir python-packages && cd python-packages

# Скачайте зависимости (на Linux)
pip download -r ../requirements.txt --platform manylinux2014_x86_64 --only-binary=:all:

# Или на другой ОС (нужно указать целевую платформу)
pip download -r ../requirements.txt --platform musllinux_1_1_x86_64 --only-binary=:all:
```

### 4. Измените Dockerfile
```Dockerfile
FROM python:3.10-alpine

# Копируем APK пакеты
COPY alpine-packages/*.apk /tmp/apk/

# Установка пакетов из локального хранилища
RUN apk add --no-cache --allow-untrusted /tmp/apk/*.apk

WORKDIR /app

# Копируем Python зависимости
COPY python-packages /tmp/pip-packages

# Устанавливаем Python пакеты
RUN pip install --no-index --find-links=/tmp/pip-packages -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### 5. Перенос файлов на целевую машину
Скопируйте всю структуру проекта включая:
- `python_image.tar`
- `postgis_image.tar`
- `alpine-packages/`
- `python-packages/`

### 6. Загрузка образов на целевой машине
```bash
docker load -i python_image.tar
docker load -i postgis_image.tar
```

### 7. Запуск проекта
```bash
docker-compose up -d
```

### Дополнительные настройки
1. Для GEOS/GDAL добавьте в Dockerfile:
```Dockerfile
ENV GEOS_LIBRARY_PATH=/usr/lib/libgeos_c.so
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
```

2. Для работы с PostGIS в Django настройки:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'mygis',
        'USER': 'postgres',
        'PASSWORD': 'mygispass',
        'HOST': 'db',
        'PORT': '5432',
    }
}
```

Важные моменты:
- Все пакеты должны быть совместимы с Alpine Linux (musl вместо glibc)
- Версии Python пакетов должны соответствовать целевой платформе
- Для ARM-архитектур потребуются соответствующие пакеты
- Проверьте совместимость версий PostGIS и PostgreSQL