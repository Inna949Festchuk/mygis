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

1. Перед запуском команды остановите службу postgresql, если она запущена (для Linux и MacOS)
```bash
sudo systemctl stop postgresql 
sudo systemctl disable postgresql
``` 
2. Запустите команду 
```bash
docker-compose up -d --build
```
3. Зайти в контейнер с помощью команды 
```bash
docker exec -it mygis-app-1 sh
```
4. Выполните команду 
```bash
python manage.py migrate
```
5. После этого вызовите оболочку Django для загрузки данных из шейп-файла
```python
python manage.py shell
```
6. Далее импортируем модуль `load`, вызываем процедуру `run` и наблюдаем, как LayerMapping выполняет свою работу
```python
from gisapp import load
load.run()
```