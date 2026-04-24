from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class MariaDBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

    def redacted(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": "***" if self.password else "",
            "database": self.database,
        }


def load_mariadb_config(env: dict[str, str] | None = None) -> MariaDBConfig:
    source = env if env is not None else os.environ
    missing = [
        name
        for name in ("TOONFLOW_DB_HOST", "TOONFLOW_DB_USER", "TOONFLOW_DB_PASSWORD", "TOONFLOW_DB_NAME")
        if not source.get(name)
    ]
    if missing:
        raise ValueError(f"Missing MariaDB config: {', '.join(missing)}")

    return MariaDBConfig(
        host=source["TOONFLOW_DB_HOST"],
        port=int(source.get("TOONFLOW_DB_PORT", "3306")),
        user=source["TOONFLOW_DB_USER"],
        password=source["TOONFLOW_DB_PASSWORD"],
        database=source["TOONFLOW_DB_NAME"],
    )


def connect_mariadb(config: MariaDBConfig | None = None) -> Any:
    try:
        import mariadb
    except ImportError as exc:
        raise RuntimeError(
            "MariaDB connector is not installed. Install MariaDB Connector/C, then install requirements-mariadb.txt."
        ) from exc

    cfg = config or load_mariadb_config()
    return mariadb.connect(
        host=cfg.host,
        port=cfg.port,
        user=cfg.user,
        password=cfg.password,
        database=cfg.database,
    )
