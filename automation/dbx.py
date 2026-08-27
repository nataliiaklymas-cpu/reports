"""
Databricks Connection Class (CI-safe).

Reads the token from the DATABRICKS_TOKEN environment variable first
(GitHub Actions secret), falling back to a local .env file for
interactive/local runs. Same public interface as the original dbx.py
used across the "Databricks & QBRs 2" workspace.
"""

import os
from pathlib import Path
from typing import Optional

from databricks import sql
import pandas as pd

SERVER_HOSTNAME = os.environ.get("DATABRICKS_SERVER_HOSTNAME", "bolt-incentives.cloud.databricks.com")
HTTP_PATH = os.environ.get("DATABRICKS_HTTP_PATH", "sql/protocolv1/o/2472566184436351/0505-112942-d3yviznw")


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


class DBX:
    """Databricks connection wrapper that returns pandas DataFrames."""

    def __init__(self, http_path: Optional[str] = None):
        self.conn = sql.connect(
            server_hostname=SERVER_HOSTNAME,
            http_path=http_path or HTTP_PATH,
            access_token=_load_token(),
        )
        with self.conn.cursor() as cur:
            cur.execute("USE CATALOG main")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def query(self, q: str, params=None) -> pd.DataFrame:
        with self.conn.cursor() as cur:
            cur.execute(q, params or None)
            columns = [desc[0] for desc in cur.description]
            return pd.DataFrame(cur.fetchall(), columns=columns)

    def close(self):
        self.conn.close()
