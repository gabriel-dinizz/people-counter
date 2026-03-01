import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

DB_PATH = Path(__file__).parent / "queue.db"


def _init_db(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pending_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id TEXT NOT NULL,
            direction TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conn.commit()


def send_event(config, direction):
    """POST a crossing event to the backend server.

    Args:
        config: ``AgentConfig`` providing ``server_url`` and ``camera_id``.
        direction: ``"entry"`` or ``"exit"``.

    Returns:
        ``True`` if the server responded with HTTP 200, ``False`` on
        any network or server error.
    """
    try:
        resp = requests.post(
            f"{config.server_url}/events",
            data={"camera_id": config.camera_id, "direction": direction},
            timeout=5,
        )
        return resp.status_code == 200
    except requests.RequestException:
        return False


def _queue_event(config, direction):
    """Write a failed event to the local SQLite queue."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        _init_db(conn)
        conn.execute(
            "INSERT INTO pending_events (camera_id, direction, timestamp) VALUES (?, ?, ?)",
            (config.camera_id, direction, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()


def send_or_queue(config, direction):
    """Attempt to send a crossing event; fall back to the local queue on failure.

    Args:
        config: ``AgentConfig`` providing server and camera details.
        direction: ``"entry"`` or ``"exit"``.

    Returns:
        ``True`` if the event was delivered to the server, ``False``
        if it was queued for later retry.
    """
    if send_event(config, direction):
        return True
    _queue_event(config, direction)
    return False


def _flush_queue(config):
    """Try to send all queued events. Delete on success, increment attempts on failure."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        _init_db(conn)
        rows = conn.execute(
            "SELECT id, camera_id, direction FROM pending_events ORDER BY id"
        ).fetchall()

        for row_id, camera_id, direction in rows:
            try:
                resp = requests.post(
                    f"{config.server_url}/events",
                    data={"camera_id": camera_id, "direction": direction},
                    timeout=5,
                )
                if resp.status_code == 200:
                    conn.execute("DELETE FROM pending_events WHERE id = ?", (row_id,))
                else:
                    conn.execute(
                        "UPDATE pending_events SET attempts = attempts + 1 WHERE id = ?",
                        (row_id,),
                    )
            except requests.RequestException:
                conn.execute(
                    "UPDATE pending_events SET attempts = attempts + 1 WHERE id = ?",
                    (row_id,),
                )
            conn.commit()


def _retry_loop(config):
    while True:
        time.sleep(30)
        _flush_queue(config)


def start_retry_thread(config):
    """Spawn a daemon thread that periodically flushes the local event queue.

    The thread retries queued events every 30 seconds. Call once at
    agent startup; the thread terminates automatically when the main
    process exits.

    Args:
        config: ``AgentConfig`` used to reach the backend server.

    Returns:
        The started ``threading.Thread`` instance.
    """
    thread = threading.Thread(target=_retry_loop, args=(config,), daemon=True)
    thread.start()
    return thread