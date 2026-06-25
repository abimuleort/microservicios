# 🐧 Penguin Academy — Python Microservices

A backend system built with **Flask** and **Docker** following a microservices architecture. The project is divided into four independent services that communicate with each other via HTTP, each with its own SQLite database and JWT-protected endpoints.

---

## 🏗️ Architecture

The system is composed of four services, all orchestrated with **Docker Compose**:

| Service | Responsibility |
|---|---|
| **Usuarios** | User registration and JWT authentication |
| **Productos** | Product catalog management |
| **Pedidos** | Order creation, linking users and products |
| **Pagos** | Payment processing, validates orders before confirming |

Each service runs in its own Docker container and communicates with the others via internal HTTP calls, forwarding JWT tokens in the `Authorization` header for authentication.

---

## 🛠️ Technologies

- **Python 3 + Flask** — REST API for each service
- **SQLite** — independent database per service
- **JWT (JSON Web Tokens)** — authentication and inter-service authorization
- **Docker + Docker Compose** — containerization and orchestration

---

## ▶️ How to Run

Make sure Docker Desktop is running, then from the root of the project:

```bash
docker-compose up --build
```

This builds and starts all four services simultaneously.

To stop them:

```bash
docker-compose down
```

---

## 📁 Project Structure

```
microservices/
├── services/
│   ├── usuarios/
│   ├── productos/
│   ├── pedidos/
│   └── pagos/
├── docker-compose.yml
└── .gitignore
```

Each service folder contains its own `app.py`, `Dockerfile`, and database file.

---

## 📌 Key Implementation Details

- All Flask services bind to `host='0.0.0.0'` to be reachable within the Docker network.
- Inter-service requests forward the `Authorization: Bearer <token>` header to propagate authentication.
- Endpoints use `request.get_json(force=True)` for compatibility with tools like Postman.
- Each service exposes its own set of REST endpoints (CRUD operations) testable via Postman.

---

*Project developed as part of the Penguin Academy backend development curriculum.*
