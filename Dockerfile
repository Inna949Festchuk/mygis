# # # Устанавливаем базовый образ Python и Alpine Linux
# # FROM python:3.10-alpine

# # # Установка компилятора gcc, библиотек GEOS, GDAL и PostgreSQL клиента для Alpine Linux
# # RUN apk add --no-cache gcc musl-dev gdal-dev geos-dev postgresql-client

# # # Устанавливаем рабочую директорию в контейнере
# # WORKDIR /app

# # # Копируем файл requirements.txt локального проекта в WORKDIR контейнера
# # COPY ./requirements.txt ./requirements.txt

# # # Устанавливаем зависимости
# # RUN pip install -r requirements.txt

# # # Указываем порт, который будет слушать сервер
# # EXPOSE 8000

# # # Копируем файлы локального проекта в WORKDIR контейнера
# # COPY . .

# # # Команда на запуск сервера
# # # CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# # CMD ["sh", "-c", "python manage.py migrate"]


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
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Клонируем стабильную версию стилей (v4.25.0 - последняя совместимая с osm2pgsql 1.8.0)
RUN git clone --branch v4.25.0 --depth 1 \
    https://github.com/gravitystorm/openstreetmap-carto.git \
    /usr/share/openstreetmap-carto

# Генерируем XML стиль (требуется для старой версии)
RUN cd /usr/share/openstreetmap-carto && \
    npm install -g carto@1.2.0 && \
    carto project.mml > mapnik.xml

# Создаем симлинк для .style файла
RUN ln -s /usr/share/openstreetmap-carto/openstreetmap-carto.style /usr/share/openstreetmap-carto.style

# Устанавливаем зависимости Python
COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . /app

# Запускаем приложение
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]