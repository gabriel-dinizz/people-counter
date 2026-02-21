# People Counter

A computer vision service that counts people in camera feeds using YOLOv8, stores the results in PostgreSQL, and exposes them via a REST API.

## Project Structure

```
people-counter/
├── .env                        # Local environment variables (not committed)
├── .env.example                # Template for environment variables
├── alembic.ini                 # Alembic configuration (run migrations from here)
├── docker-compose.yml          # PostgreSQL database service
├── requirements.txt
└── app/
    ├── alembic/                # Database migrations
    │   └── versions/
    ├── api/
    │   └── routes.py           # FastAPI route definitions
    ├── core/
    │   ├── detector.py         # YOLOv8 people detection
    │   └── preprocessor.py     # Frame preprocessing
    ├── db/
    │   ├── database.py         # SQLAlchemy engine and session
    │   ├── models.py           # ORM models
    │   └── repository.py       # Database query logic
    ├── pipeline/
    │   └── service.py          # Detection pipeline orchestration
    ├── config.py               # Pydantic settings
    └── main.py                 # FastAPI application entry point
```

## Tech Stack

- **Python 3.13**
- **YOLOv8** — people detection
- **FastAPI** — REST API
- **PostgreSQL 16** — data storage
- **SQLAlchemy 2** — ORM
- **Alembic** — database migrations
- **Pydantic Settings** — configuration management
- **Docker Compose** — local database

## Prerequisites

- Python 3.13
- Docker Desktop
- (Optional) PgAdmin for database inspection

## Setup

### 1. Create virtual environment and install dependencies

> **macOS note:** use `python3` (or `python3.13`) explicitly — `python` may not exist or point to an older version.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
POSTGRES_USER=people_counter
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=people_counter
DATABASE_URL=postgresql://people_counter:your_password_here@localhost:5432/people_counter
```

### 3. Start the database

```bash
docker compose up -d
```

### 4. Run database migrations

Always run Alembic from the project root:

```bash
alembic upgrade head
```

## Database Migrations

All Alembic commands must be run from the project root (`people-counter/`).

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Database Schema

### `people_counts`

| Column         | Type        | Description                        |
|----------------|-------------|------------------------------------|
| `id`           | Integer PK  | Auto-incremented primary key       |
| `camera_id`    | String(64)  | Identifier for the camera source   |
| `timestamp`    | DateTime    | When the count was recorded        |
| `people_count` | Integer     | Number of people detected          |
| `event`        | String(64)  | Event type (default: `snapshot`)   |

## PgAdmin Connection

| Field    | Value            |
|----------|------------------|
| Host     | `localhost`      |
| Port     | `5432`           |
| Database | `people_counter` |
| Username | `people_counter` |
| Password | *(from `.env`)*  |

## Notes

- If you have a local PostgreSQL running on port 5432, stop it before starting Docker: `brew services stop postgresql@15`
- The `.env` file is never committed — use `.env.example` as the reference template
