# 📝 FastAPI Todo App (Users + Auth)

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)  
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](https://fastapi.tiangolo.com/)  
[![Docker](https://img.shields.io/badge/Docker-24.0-blue?logo=docker)](https://www.docker.com/)

A **backend API for a Todo application** built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy**, supporting **users, authentication, and user-owned todos**.  

This project is structured for **scalability, testing, and real-world production patterns**, while being beginner-friendly for those learning FastAPI.

---

## 🚀 Features

- **User Management**: register, login, view profile  
- **Todo Management**: create, update, delete, and list todos (per user)  
- **Authentication**: JWT-based token system  
- **Authorization**: users can only access their own todos  
- **Database Migrations**: Alembic-managed  
- **Containerized**: Docker + Docker Compose setup  
- **Testing**: Pytest-ready tests for all endpoints  

---

## 📂 Project Structure

```
backend/
├── app/
│   ├── main.py
│   ├── core/           # Config, database, security, logging
│   ├── api/            # Routes & dependencies
│   ├── models/         # Database tables
│   ├── schemas/        # Pydantic validation
│   ├── crud/           # Database operations
│   ├── services/       # Business logic
│   ├── middleware/     # Request interceptors
│   └── utils/          # Shared helpers
├── tests/              # Automated tests
├── alembic/            # Migrations
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
└── README.md
```

---

## 📷 Screenshots

> Replace these with actual images of API docs, sample requests/responses, or terminal outputs.  

![API Docs Placeholder](docs/api_docs_placeholder.png)

---

## 🐣 Getting Started (for beginners)

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd backend
```

---

### 2. Create `.env` file

Example `.env`:

```
DATABASE_URL=postgresql://postgres:postgres@db:5432/todos
SECRET_KEY=supersecret
```

---

### 3. Start the project with Docker

```bash
docker-compose up --build
```

This runs **FastAPI + PostgreSQL** containers.

---

### 4. Apply database migrations

```bash
docker-compose exec backend alembic upgrade head
```

---

### 5. Explore API docs

Open your browser:

```
http://localhost:8000/docs
```

---

### 6. Run tests

```bash
pytest
```

---

## 🧠 How it works

```
Request
 → API route
 → Service (business rules)
 → CRUD (database)
 → Schema (validation)
 → Response
```

---

## 🎯 Purpose

- Learn **real backend architecture**  
- Practice **clean separation of concerns**  
- Build a **production-ready, multi-user FastAPI backend**  

---

## 🛠️ Tips for Extending

- Add **user roles** (admin, regular user)  
- Add **background tasks** with Celery  
- Add **rate limiting or logging enhancements**  
- Connect **frontend apps** with this API (React, Next.js, Vue)  
