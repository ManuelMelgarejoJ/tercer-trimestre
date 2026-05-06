#!/bin/sh

# Esperar a que la base de datos esté lista
if [ "$POSTGRES_HOST" ]; then
    echo "Esperando a la base de datos en $POSTGRES_HOST:5432..."
    while ! nc -z $POSTGRES_HOST 5432; do
      sleep 0.1
    done
    echo "¡Base de datos lista!"
fi

# Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py migrate --noinput

# Recolectar archivos estáticos (opcional, útil para producción)
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Ejecutar el comando pasado al contenedor (gunicorn o runserver)
exec "$@"
