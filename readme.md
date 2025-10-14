# Filtering Service - Multi tenant

Filtering service for message before send to LLM model. using pyhon Python 3.12.7 and pip
pip 24.2

---

## Fitur Utama

- **Upload External Dict:** Upload data with format json as a base dictionary
- **Support Slang, Sentiment and Badwords:** you can choose what do you need
- **Cache and performance:** Store and reuse dictionary to better performance

---

## 🛠️ Teknologi yang Digunakan

- **Runtime:** Uvicorn
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Cache:** Redis
- **Containerization:** Docker

---

## ⚙️ Panduan Instalasi Lokal

**1. Development mode**

- git clone repository
- cd chatbot-ai-service
- python -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt
- uvicorn app.main:app --host 0.0.0.0 --port 8000

**2. Image mode**

- docker-compose up -d

---

## 📚 Dokumentasi API

**1. Health check**
GET http://localhost:8000/health
