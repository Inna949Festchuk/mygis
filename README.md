python3 -m venv venv

source venv/bin/activate

pip3 install django

pip3 freeze > requirements.txt

django-admin startproject gisproject .

python3 manage.py startapp gisapp



# РАЗВОРАЧИВАЕМ ПРИЛОЖЕНИЕ:

Создаем виртуальную среду, активируем ее и устанавливаем все зависимости
---
python3 -m venv venv

source venv/bin/activate

python3 -m pip install -r requirements.txt


# УСТАНАВЛИВАЕМ И НАСТРАИВАЕМ PostgreSQL+PostGIS

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


