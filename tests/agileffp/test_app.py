import pytest
from starlette.testclient import TestClient

from agileffp.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "AgileFFP - by Javier Carnero" in response.text
