"""
Databricks Connection Class (CI-safe).

Reads the token from the DATABRICKS_TOKEN environment variable first
(GitHub Actions secret), falling back to a local .env file for
interactive/local runs. Same public interface as the original dbx.py
used across the "Databricks & QBRs 2" workspace.
"""

import os
import time
from pathlib import Path
from typing import Optional

from databricks import sql
from databricks.sql.exc import (
    CursorAlreadyClosedError,
    DatabaseError,
    OperationalError,
    RequestError,
    ServerOperationError,
    SessionAlreadyClosedError,
)
import pandas as pd

SERVER_HOSTNAME = os.environ.get("DATABRICKS_SERVER_HOSTNAME", "bolt-incentives.cloud.databricks.com")
HTTP_PATH = os.environ.get("DATABRICKS_HTTP_PATH", "sql/protocolv1/o/2472566184436351/0505-112942-d3yviznw")

_RETRYABLE_MARKERS = (
    "invalid operationhandle",
    "invalid sessionhandle",
    "session that was already closed",
    "temporarily unavailable",
    "connection reset",
    "broken pipe",
    "timeout",
    "timed out",
    "eof",
)

_RETRYABLE_EXC = (
    DatabaseError,
    RequestError,
    ServerOperationError,
    SessionAlreadyClosedError,
    CursorAlreadyClosedError,
    OperationalError,
    OSError,
    TimeoutError,
)


def _load_token() -> str:
    env_token = os.environ.get("DATABRICKS_TOKEN")
    if env_token:
        return env_token.strip()
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("DATABRICKS_TOKEN="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError(
        "DATABRICKS_TOKEN not found. Set it as an environment variable "
        "(GitHub Actions secret) or create a local .env file."
    )


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, (SessionAlreadyClosedError, CursorAlreadyClosedError)):
        return True
    msg = str(exc).lower()
    return any(marker in msg for marker in _RETRYABLE_MARKERS)


class DBX:
    """Databricks connection wrapper that returns pandas DataFrames."""

    def __init__(self, http_path: Optional[str] = None):
        self.http_path = http_path or HTTP_PATH
        self.conn = None
        self._connect()

    def _connect(self):
        if self.conn is not None:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None
        self.conn = sql.connect(
            server_hostname=SERVER_HOSTNAME,
            http_path=self.http_path,
            access_token=_load_token(),
        )
        with self.conn.cursor() as cur:
            cur.execute("USE CATALOG main")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def query(self, q: str, params=None, attempts: int = 4) -> pd.DataFrame:
        last_err = None
        for attempt in range(1, attempts + 1):
            try:
                with self.conn.cursor() as cur:
                    cur.execute(q, params or None)
                    columns = [desc[0] for desc in cur.description]
                    return pd.DataFrame(cur.fetchall(), columns=columns)
            except _RETRYABLE_EXC as exc:
                last_err = exc
                if attempt >= attempts or not _is_retryable(exc):
                    raise
                wait = min(2 ** attempt, 20)
                print(
                    f"[WARN] Databricks query failed (attempt {attempt}/{attempts}), "
                    f"reconnecting in {wait}s: {exc}"
                )
                time.sleep(wait)
                self._connect()
        raise last_err

    def close(self):
        if self.conn is None:
            return
        try:
            self.conn.close()
        except Exception:
            pass
        self.conn = None
