FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalamos netcat para el entrypoint y dependencias de postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    netcat-openbsd \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Configurar el entrypoint
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

# Comando por defecto (puede ser sobrescrito por docker-compose)
CMD ["gunicorn", "steamlike_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
