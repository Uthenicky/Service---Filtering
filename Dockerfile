# Stage 1: Build stage with all dependencies
FROM python:3.11-slim as builder

WORKDIR /usr/src/app

# Mencegah Python menulis file .pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Memastikan output dari Python tidak di-buffer
ENV PYTHONUNBUFFERED 1

# Install dependensi
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# --- Stage 2: Production image ---
FROM python:3.11-slim

WORKDIR /app

# Buat user non-root untuk keamanan
RUN addgroup --system app && adduser --system --group app

# Salin dependensi yang sudah di-build
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Salin kode aplikasi
COPY ./app /app/app

# Ganti kepemilikan file ke user non-root
RUN chown -R app:app /app
USER app

# Jalankan aplikasi dengan Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]