import pytest
from fasthtml.common import database, fast_app
from starlette.testclient import TestClient

from agileffp.app import app
from agileffp.project import model


@pytest.fixture(scope="session")
def test_db():
    """Create an in-memory SQLite database for testing."""
    db = database(":memory:")

    # Initialize the project model with the test database
    model.init(db)

    # Create a test project
    model.create_project("test_project", "Test project for testing")

    return db


@pytest.fixture
def client(test_db):
    """Return a TestClient instance for the app."""
    # Use the app imported directly (which has the real DB setup)
    # The model module should be patched to use our test_db
    return TestClient(app)


@pytest.fixture
def test_app(test_db):
    """Create a fresh FastAPI app instance with the test database."""
    test_app, _ = fast_app()
    return test_app