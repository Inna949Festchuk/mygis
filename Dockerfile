# Устанавливаем базовый образ Python и Alpine Linux
FROM python:3.10-alpine

# Установка компилятора gcc, библиотек GEOS, GDAL и PostgreSQL клиента для Alpine Linux
RUN apk add --no-cache gcc musl-dev gdal-dev geos-dev postgresql-client

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл requirements.txt локального проекта в WORKDIR контейнера
COPY ./requirements.txt ./requirements.txt

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Указываем порт, который будет слушать сервер
EXPOSE 8000

# Копируем файлы локального проекта в WORKDIR контейнера
COPY . .

# Команда на запуск сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]