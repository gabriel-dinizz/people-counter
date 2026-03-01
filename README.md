# People Counter

An edge-computing people counter that uses YOLOv8 to detect people crossing a virtual line in a camera feed, reports entry/exit events to a FastAPI backend, and stores them in PostgreSQL for occupancy queries.

## Architecture

```
┌──────────────────┐         POST /events         ┌──────────────────┐
│   Edge Agent     │ ──────────────────────────▶   │   FastAPI API    │
│  (YOLOv8 + CV2)  │   ◀── GET /occupancy/{id} ── │  + PostgreSQL    │
└──────────────────┘                               └──────────────────┘
```

- **Edge agent** — captures camera frames, tracks people with YOLOv8, detects line crossings, and sends events to the backend. Queues events locally (SQLite) when the server is unreachable.
- **Backend API** — receives crossing events, persists them in PostgreSQL, and exposes an occupancy endpoint.

## Project Structure

```
people-counter/
├── .env.example                # Template for environment variables
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # PostgreSQL service
├── requirements.txt
└── app/
    ├── main.py                 # FastAPI application entry point
    ├── config.py               # Pydantic settings (backend)
    ├── api/
    │   └── routes.py           # POST /events, GET /occupancy/{camera_id}
    ├── db/
    │   ├── database.py         # SQLAlchemy engine and session
    │   ├── models.py           # CrossingEvent ORM model
    │   └── repository.py       # Data access layer
    ├── alembic/
    │   └── versions/           # Database migrations
    └── agent/
        ├── main.py             # Detection loop entry point
        ├── config.py           # AgentConfig dataclass
        ├── config.yaml         # Agent settings (camera, line, model)
        ├── capture.py          # Camera capture (device/file/RTSP)
        ├── tracker.py          # YOLOv8 people tracking
        ├── crossing.py         # Line crossing detection
        ├── display.py          # OpenCV visualization overlays
        ├── sender.py           # Event sending with offline queue
        └── calibrate.py        # Interactive line calibration tool
```

## Tech Stack

- **Python 3.13**
- **YOLOv8** (ultralytics) — people detection and tracking
- **OpenCV** — camera capture and visualization
- **FastAPI** + **Uvicorn** — REST API
- **PostgreSQL 16** — event storage
- **SQLAlchemy 2** — ORM
- **Alembic** — database migrations
- **Pydantic Settings** — configuration management
- **Docker Compose** — local database

## Prerequisites

- Python 3.13
- Docker Desktop
- A camera source (webcam, video file, or RTSP stream)

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

```bash
alembic upgrade head
```

### 5. Start the backend API

```bash
uvicorn app.main:app --reload
```

### 6. Configure and run the edge agent

Edit `app/agent/config.yaml`:

```yaml
camera_id: entrance-main
camera_source: 0                    # 0 for webcam, or a video file / RTSP URL
server_url: http://localhost:8000
yolo_model: yolov8n.pt
yolo_confidence: 0.4
line:
  start: [398, 633]
  end: [1472, 854]
```

Use the calibration tool to interactively set the crossing line:

```bash
cd app && python -m agent.calibrate
```

Click two points to define the line, press `s` to save, `r` to reset, `q` to quit.

Then run the agent:

```bash
cd app && python -m agent.main
```

Add `--show` to open a live window with detection overlays:

```bash
cd app && python -m agent.main --show
```

## API Endpoints

### `POST /events`

Record a crossing event.

| Parameter    | Type   | Description              |
|-------------|--------|--------------------------|
| `camera_id` | string | Camera identifier        |
| `direction` | string | `"entry"` or `"exit"`    |

### `GET /occupancy/{camera_id}`

Returns current occupancy (entries minus exits, minimum 0).

```json
{"camera_id": "entrance-main", "occupancy": 3}
```

## Database Schema

### `crossing_events`

| Column       | Type        | Description                        |
|-------------|-------------|------------------------------------|
| `id`        | Integer PK  | Auto-incremented primary key       |
| `camera_id` | String(64)  | Camera identifier (indexed)        |
| `timestamp` | DateTime    | When the event occurred (indexed)  |
| `direction` | String(8)   | `"entry"` or `"exit"`              |

## Database Migrations

All Alembic commands must be run from the project root.

```bash
alembic revision --autogenerate -m "description"   # create migration
alembic upgrade head                                # apply migrations
alembic downgrade -1                                # rollback one
```

## Notes

- If you have a local PostgreSQL running on port 5432, stop it before starting Docker: `brew services stop postgresql@15`
- The `.env` file is never committed — use `.env.example` as the reference template
- Swapping `line.start` and `line.end` in config.yaml flips the entry/exit direction
- The agent queues events locally in SQLite when the backend is unreachable and retries every 30 seconds
