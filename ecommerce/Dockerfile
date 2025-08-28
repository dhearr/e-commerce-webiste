FROM python:3.12-slim

# 1) sistem dasar
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 2) deps OS yg sering dibutuhin (psycopg2 lxml pillow, dll)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

# 3) install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# 4) copy source
COPY . .

# 5) buka port dev
EXPOSE 8000

# 6) jalankan dev server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
