FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Render asigna el puerto en la variable $PORT
EXPOSE 8000

# IMPORTANTE: sustituye "tercer_trimestre" por tu carpeta real
CMD gunicorn tercer_trimestre.wsgi:application --bind 0.0.0.0:$PORT
