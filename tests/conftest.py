import os
import tempfile
import pytest
import asyncio
from app.db import init_db

@pytest.fixture()
def temp_db(tmp_path, monkeypatch):
    db_file = tmp_path / 'test.db'
    # set env var for tests
    monkeypatch.setenv('DATABASE_URL', f"sqlite:///{db_file}")
    # init db
    asyncio.run(init_db())
    return str(db_file)
