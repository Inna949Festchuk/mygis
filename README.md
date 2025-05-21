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



## Linux Ubuntu 

Для установки PostGIS на Ubuntu, выполните следующие шаги:

1. **Обновите систему**:
   Перед установкой новых пакетов рекомендуется обновить список доступных пакетов:
   ```bash
   sudo apt update
   ```

2. **Установите PostgreSQL** (если его еще нет):
   Если PostgreSQL не установлен, установите его вместе с `postgresql-contrib`:
   ```bash
   sudo apt install postgresql postgresql-contrib
   ```

3. **Установите PostGIS**:
   Установите PostGIS, выполнив следующую команду:
   ```bash
   sudo apt install postgis postgresql-<version>-postgis-<version>
   ```
   Замените `<version>` на соответствующую версию PostgreSQL, которую вы установили. Например, если вы используете PostgreSQL 14, команда будет выглядеть следующим образом:
   ```bash
   sudo apt install postgis postgresql-14-postgis-3
   ```

4. **Создайте базу данных и пользователя**:
   Войдите в оболочку PostgreSQL и создайте нового пользователя и базу данных. Например:
   ```bash
   sudo -u postgres psql
   CREATE DATABASE my_spatial_db;
   CREATE USER my_spatial_user WITH PASSWORD 'my_password';
   GRANT ALL PRIVILEGES ON DATABASE my_spatial_db TO my_spatial_user;
   ```

5. **Активируйте PostGIS на базе данных**:
   Подключитесь к созданной базе данных и активируйте расширение PostGIS:
   ```bash
   \c my_spatial_db
   CREATE EXTENSION postgis;
   ```

6. **Проверьте установку**:
   Чтобы убедиться, что PostGIS установлен и работает, выполните следующую команду:
   ```bash
   SELECT PostGIS_version();
   ```
   Вы должны увидеть версию PostGIS, подтверждающую что оно правильно установлено.

Теперь вы можете использовать PostGIS для работы с пространственными данными в вашей базе данных PostgreSQL 