import pytest
from fasthtml.common import database
from starlette.testclient import TestClient

from agileffp.app import app
from agileffp.project import model


@pytest.fixture
def test_db():
    # Create an in-memory SQLite database for testing
    db = database(":memory:")

    # Initialize the project model with the test database
    model.init(db)

    # Mock the app database to use our test database
    yield db


@pytest.fixture
def client(test_db):
    return TestClient(app)


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "AgileFFP - a tool by Javier Carnero" in response.text
