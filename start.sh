#!/bin/bash
set -e

# Создаем папку проекта
mkdir -p mygis-project && cd mygis-project

# Клонируем репозиторий
git clone https://github.com/Inna949Festchuk/mygis.git
cd mygis

# Запускаем контейнеры
docker-compose up -d --build

# Ждем готовности PostgreSQL
echo "Ожидание инициализации БД (15 сек)..."
sleep 15

# Выполняем миграции
docker-compose exec app sh -c "python manage.py migrate"

# Загружаем данные через LayerMapping
docker-compose exec app sh -c "echo -e 'from gisapp import load\nload.run()' | python manage.py shell"

# Открываем приложение в браузере
xdg-open "http://localhost:8000/map"
