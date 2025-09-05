FROM python:3.12-bullseye

# 1) sistem dasar
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 2) deps OS untuk WeasyPrint & font rendering
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-dejavu-core \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3) install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install WeasyPrint

# 4) copy source
COPY . .

# 5) buka port dev
EXPOSE 8000

# 6) jalankan dev server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
