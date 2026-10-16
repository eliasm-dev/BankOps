# BankOps — Banking Operations & Database Monitoring System

**BankOps** is an educational full-stack project designed to demonstrate how banking IT teams can organize database infrastructure information, review backup operations, monitor system status, and track operational incidents.

The project combines a FastAPI backend, a PostgreSQL database, and a React frontend. It uses simulated data for development and learning.

> **Disclaimer:** BankOps is a demonstration project. It is not connected to a real bank, production database, or live banking infrastructure. It is not intended for production use.

## Project Overview

BankOps explores common database administration and IT operations concepts through a web-based application. It provides a foundation for learning backend development, relational database design, API development, and database monitoring workflows.

## Features

- **Authentication:** API login and token-based authentication.
- **Dashboard:** An API endpoint for retrieving operational summary information.
- **User management:** Backend user-management functionality.
- **Database inventory:** Data models for database instances and related infrastructure.
- **Backup operations:** Structures for backup jobs, backup runs, backup verification, and restore tests.
- **Monitoring and incidents:** Models for monitoring metrics and operational incident records.
- **Audit records:** Structures for recording application activity and login history.
- **Database migrations:** Schema versioning with Alembic.
- **Demo data:** Seeded records for development and testing.

*Feature availability depends on the current implementation; the project is still under development.*

## Technology Stack

| Area | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database migrations | Alembic |
| Frontend | React, Vite, JavaScript |
| Styling | Tailwind CSS |
| API documentation | OpenAPI / Swagger UI |
| Version control | Git and GitHub |

## Project Structure

```text
BankOps/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── security/
│   │   ├── services/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── main.py
│   │   └── seed.py
│   ├── alembic/
│   └── requirements.txt
├── database/
│   └── schema.sql
├── frontend/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

Install the following before running the project:

- Python and pip
- PostgreSQL
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/eliasm-dev/BankOps.git
cd BankOps
```

### 2. Configure the backend

Open a terminal in the backend directory:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configure the required environment variables in `backend/.env` according to the application's configuration. Set the PostgreSQL connection details for your own local development database.

**Do not commit `.env` files, passwords, access tokens, or other secrets to GitHub.**

### 3. Prepare the database

Create a PostgreSQL database for local development, then configure the application to connect to it.

Run the database migrations:

```powershell
python -m alembic upgrade head
```

If you want to load the sample records, run the seed command only against your dedicated demo database:

```powershell
python -m app.seed
```

**Warning:** The seed script rebuilds application data. Do not run it against a database containing data you need to preserve.

### 4. Start the backend

From the `backend` directory:

```powershell
python -m uvicorn app.main:app --reload
```

The API should be available at:

- **API base:** http://127.0.0.1:8000
- **Swagger documentation:** http://127.0.0.1:8000/api/docs
- **Health endpoint:** http://127.0.0.1:8000/api/health

The health endpoint can be used to check whether the application is responding.

### 5. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite in the terminal. Ensure the frontend's API configuration points to the backend running on `http://127.0.0.1:8000`.

## Development and Testing

BankOps is intended to support hands-on practice with:

- Designing relational database schemas.
- Building REST APIs with FastAPI.
- Connecting Python applications to PostgreSQL.
- Managing schema changes with Alembic.
- Implementing authentication and API authorization.
- Modeling backup, restore, and monitoring workflows.
- Using Git and GitHub to manage a development project.

Use the interactive Swagger documentation to explore the API. Not every endpoint has been fully tested, and some functionality may require further development.

## Security Considerations

This project is for local learning and demonstration purposes.

- Use synthetic data only.
- Keep credentials and secret keys out of source control.
- Use a dedicated local database for development.
- Do not connect the application to real banking systems.
- Do not expose development services to public networks.
- Implement and thoroughly test additional security controls before considering any production deployment.

## Current Status

**Status:** Active development

The initial project version has been published to GitHub. Backend verification, endpoint testing, frontend integration, and further improvements are ongoing.

## Author

**Elias Moges**

BSc in Information Systems | Graduate Trainee Database Administrator | Aspiring Backend Developer

GitHub: [@eliasm-dev](https://github.com/eliasm-dev)

Project repository: [BankOps](https://github.com/eliasm-dev/BankOps)

---

*Built as a practical learning project at the intersection of database administration, backend development, and banking IT operations.*