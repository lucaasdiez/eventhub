# --------------------------------------
# ETAPA 1: Constructor (builder)
# --------------------------------------
FROM python:3.11-slim AS builder

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar herramientas necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# --------------------------------------
# ETAPA 2: Producción
# --------------------------------------
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=eventhub.settings

WORKDIR /app

# Instalar netcat para wait-for.sh si lo usás
RUN apt-get update && apt-get install -y netcat && rm -rf /var/lib/apt/lists/*

# Instalar Python deps desde la etapa anterior
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copiar el proyecto completo
COPY . .

# (Opcional) Esperar a DB antes de arrancar si usás PostgreSQL o similar
COPY ./wait-for.sh /wait-for.sh
RUN chmod +x /wait-for.sh

# Ejecutar migraciones y recolectar archivos estáticos
# Render ejecuta CMD en runtime, así que migraciones deberían ir en el entrypoint o directamente en tu start script
RUN python manage.py collectstatic --no-input

EXPOSE 8000

# Comando final (usa wait-for.sh si hace falta esperar DB)
CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "eventhub.wsgi"]
