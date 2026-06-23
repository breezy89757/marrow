import pytest
from pathlib import Path
from marrow.database import init_db

@pytest.fixture
def temp_db(tmp_path) -> Path:
    db_file = tmp_path / "test_marrow.db"
    init_db(db_file)
    return db_file
