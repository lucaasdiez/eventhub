#!/bin/sh
set -e
echo "Ejecutando migraciones de la base de datos..."
python manage.py migrate --no-input
echo "Iniciando el servidor Gunicorn..."
exec gunicorn --workers 1 eventhub.wsgi:application