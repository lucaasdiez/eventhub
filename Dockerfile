# --------------------------------------
# ETAPA 1: Constructor (builder)
# --------------------------------------
FROM python:3.11-slim as builder

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instalar dependencias del sistema básicas
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# --------------------------------------
# ETAPA 2: Producción
# --------------------------------------
FROM python:3.11-slim

WORKDIR /app

# Copiar dependencias instaladas desde builder
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copiar aplicación
COPY . .

# Configurar variables de entorno
ENV DJANGO_SETTINGS_MODULE=eventhub.settings

# Ejecutar migraciones y recolección de estáticos
RUN python manage.py migrate --no-input && \
    python manage.py collectstatic --no-input

# Exponer puerto y ejecutar
EXPOSE 8000
CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "eventhub.wsgi"]