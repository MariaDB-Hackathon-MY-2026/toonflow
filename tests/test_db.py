import sys

import pytest

from toonflow.db import MariaDBConfig, connect_mariadb, load_mariadb_config


def env():
    return {
        "TOONFLOW_DB_HOST": "localhost",
        "TOONFLOW_DB_PORT": "3307",
        "TOONFLOW_DB_USER": "toonflow",
        "TOONFLOW_DB_PASSWORD": "example-password",
        "TOONFLOW_DB_NAME": "toonflow_test",
    }


def test_load_mariadb_config_from_env_mapping():
    config = load_mariadb_config(env())
    assert config.host == "localhost"
    assert config.port == 3307
    assert config.user == "toonflow"
    assert config.database == "toonflow_test"


def test_load_mariadb_config_reports_missing_values():
    with pytest.raises(ValueError, match="TOONFLOW_DB_PASSWORD"):
        load_mariadb_config({"TOONFLOW_DB_HOST": "localhost", "TOONFLOW_DB_USER": "toonflow", "TOONFLOW_DB_NAME": "db"})


def test_config_redacts_password():
    config = MariaDBConfig(host="h", port=3306, user="u", password="p", database="d")
    assert config.redacted()["password"] == "***"


def test_connect_mariadb_gives_actionable_error_when_connector_missing(monkeypatch):
    monkeypatch.setitem(sys.modules, "mariadb", None)
    with pytest.raises(RuntimeError, match="MariaDB connector is not installed"):
        connect_mariadb(MariaDBConfig(host="h", port=3306, user="u", password="p", database="d"))
