# # Устанавливаем базовый образ Python и Alpine Linux
# FROM python:3.10-alpine

# # Установка компилятора gcc, библиотек GEOS, GDAL и PostgreSQL клиента для Alpine Linux
# RUN apk add --no-cache gcc musl-dev gdal-dev geos-dev postgresql-client

# # Устанавливаем рабочую директорию в контейнере
# WORKDIR /app

# # Копируем файл requirements.txt локального проекта в WORKDIR контейнера
# COPY ./requirements.txt ./requirements.txt

# # Устанавливаем зависимости
# RUN pip install -r requirements.txt

# # Указываем порт, который будет слушать сервер
# EXPOSE 8000

# # Копируем файлы локального проекта в WORKDIR контейнера
# COPY . .

# # Команда на запуск сервера
# # CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# CMD ["sh", "-c", "python manage.py migrate"]


# Используем официальный образ Python
FROM python:3.11

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y \
    gdal-bin \
    binutils \
    libproj-dev \
    libgdal-dev \
    libgeos-dev \
    postgresql-client \
    osm2pgsql \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости Python
COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . /app

# Запускаем приложение 
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "gisproject.wsgi:application"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]