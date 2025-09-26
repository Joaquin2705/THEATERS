# Imagen base ligera
FROM python:3.12-slim

# Evitar bytecode y buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Crear directorio de app
WORKDIR /app

# Instalar dependencias del sistema (watchdog necesita inotify en linux ya incluido)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY app ./app

# Crear carpeta para datos (DB) dentro del contenedor
RUN mkdir -p /app/data

# Puerto de la app
EXPOSE 8001

# Variable por defecto de la DB (usa carpeta /app/data que montaremos)
ENV DATABASE_URL=sqlite:///./data/theaters.db

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
