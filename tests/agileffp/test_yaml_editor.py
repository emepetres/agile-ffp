from io import BytesIO

import pytest
from fasthtml.common import database, fast_app
from starlette.testclient import TestClient

from agileffp.monitor.routes import Endpoints, init
from agileffp.project import model


@pytest.fixture
def test_db():
    # Create an in-memory SQLite database for testing
    db = database(":memory:")

    # Initialize the project model with the test database
    model.init(db)

    return db


@pytest.fixture
def yaml_editor_client(test_app, test_db, monkeypatch):
    """Create a test client for YAML editor tests."""
    # Set up test YAML content
    test_yaml = """
iterations:
  - name: Sample Iteration
    points: 100
    stories:
      - name: User Story 1
        points: 25
        status: Completed

epics:
  - name: Sample Epic
    points: 50
    priority: High
"""

    # Mock the get_yaml_version_context method to return test data
    def mock_get_yaml_context(project_name, version=None):
        return "current_version", test_yaml, "prev_version", "next_version"

    monkeypatch.setattr(model, "get_yaml_version_context",
                        mock_get_yaml_context)

    # Initialize monitor module with a test charts container ID
    init(test_app, "charts_container_id")
    test_client = TestClient(test_app)

    # Set the HX-Current-URL header to simulate being in a project context
    test_client.headers = {"hx-current-url": "/project/test_project"}

    return test_client


@pytest.fixture
def sample_yaml():
    return """
    name: test
    items:
      - id: 1
        value: foo
      - id: 2
        value: bar
    """


@pytest.fixture
def ordered_yaml():
    return """
charlie: 3
alpha: 1
beta: 2
nested:
  zebra: 26
  monkey: 13
  aardvark: 1
animals:
  - zebra
  - monkey
  - aardvark
config:
  timeout: 30
  name: "test"
  enabled: true
"""


def test_set_yaml_success(yaml_editor_client, sample_yaml):
    file = BytesIO(sample_yaml.encode("utf-8"))
    response = yaml_editor_client.put(
        Endpoints.UPLOAD.with_prefix(),
        files={"file": ("test.yaml", file, "text/yaml")},
        headers={"hx-current-url": "/project/test_project"}
    )

    assert response.status_code == 200
    assert "name: test" in response.text
    assert "items:" in response.text
    assert "value: foo" in response.text


def test_set_yaml_no_file(yaml_editor_client):
    response = yaml_editor_client.put(
        Endpoints.UPLOAD.with_prefix(),
        headers={"hx-current-url": "/project/test_project"}
    )
    assert response.status_code == 200
    assert "No content loaded" in response.text


def test_set_yaml_invalid_yaml(yaml_editor_client):
    invalid_yaml = """
    bad: [
      unclosed bracket
    """
    file = BytesIO(invalid_yaml.encode("utf-8"))
    response = yaml_editor_client.put(
        Endpoints.UPLOAD.with_prefix(),
        files={"file": ("invalid.yaml", file, "text/yaml")},
        headers={"hx-current-url": "/project/test_project"}
    )

    assert response.status_code == 200
    assert "Invalid YAML format" in response.text


def test_load_template(yaml_editor_client, monkeypatch):
    # Mock the template function to return a known value
    template_content = """
iterations:
  - name: Sample Iteration
    points: 100
epics:
  - name: Sample Epic
    points: 50
"""
    monkeypatch.setattr("agileffp.monitor.views.yaml_editor.get_default_template",
                        lambda: template_content)

    response = yaml_editor_client.put(
        Endpoints.UPLOAD_TEMPLATE.with_prefix(),
        headers={"hx-current-url": "/project/test_project"}
    )

    assert response.status_code == 200
    assert "iterations:" in response.text
    assert "epics:" in response.text


def test_set_yaml_preserves_order(yaml_editor_client, ordered_yaml):
    file = BytesIO(ordered_yaml.encode("utf-8"))
    response = yaml_editor_client.put(
        Endpoints.UPLOAD.with_prefix(),
        files={"file": ("test.yaml", file, "text/yaml")},
        headers={"hx-current-url": "/project/test_project"}
    )

    assert response.status_code == 200
    content = response.text

    # Check order of top-level keys (non-alphabetical)
    charlie_pos = content.find("charlie:")
    alpha_pos = content.find("alpha:")
    beta_pos = content.find("beta:")
    assert charlie_pos < alpha_pos < beta_pos

    # Check order of nested keys (non-alphabetical)
    zebra_pos = content.find("zebra:")
    monkey_pos = content.find("monkey:")
    aardvark_pos = content.find("aardvark:")
    assert zebra_pos < monkey_pos < aardvark_pos

    # Check order of list items (non-alphabetical)
    zebra_list_pos = content.find("- zebra")
    monkey_list_pos = content.find("- monkey")
    aardvark_list_pos = content.find("- aardvark")
    assert zebra_list_pos < monkey_list_pos < aardvark_list_pos


def test_endpoints_prefix():
    from agileffp.monitor.routes import Endpoints

    app, _ = fast_app()
    init(app, None, prefix="/test")

    assert Endpoints.UPLOAD.with_prefix() == "/test" + Endpoints.UPLOAD.value
