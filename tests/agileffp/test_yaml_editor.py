from asyncio import Queue
from io import BytesIO

import pytest
from fasthtml.common import fast_app
from starlette.testclient import TestClient

from agileffp.yaml_editor.api import build_api
from agileffp.yaml_editor.config import Endpoints


@pytest.fixture
def client():
    app, _ = fast_app()
    build_api(app, Queue())
    test_client = TestClient(app)
    test_client.put(Endpoints.RESET.with_prefix())
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


def test_set_yaml_success(client, sample_yaml):
    file = BytesIO(sample_yaml.encode("utf-8"))
    response = client.put(
        Endpoints.UPLOAD.with_prefix(), files={"file": ("test.yaml", file, "text/yaml")}
    )

    assert response.status_code == 200
    assert "File: test.yaml" in response.text
    assert "name: test" in response.text
    assert "items:" in response.text
    assert "value: foo" in response.text


def test_set_yaml_no_file(client):
    response = client.put(Endpoints.UPLOAD.with_prefix())
    assert response.status_code == 200
    assert "No content loaded" in response.text


def test_set_yaml_invalid_yaml(client):
    invalid_yaml = """
    bad: [
      unclosed bracket
    """
    file = BytesIO(invalid_yaml.encode("utf-8"))
    response = client.put(
        Endpoints.UPLOAD.with_prefix(),
        files={"file": ("invalid.yaml", file, "text/yaml")},
    )

    assert response.status_code == 200
    assert "Invalid YAML format" in response.text


def test_load_template(client):
    response = client.put(Endpoints.UPLOAD_TEMPLATE.with_prefix())

    assert response.status_code == 200
    assert "iterations:" in response.text
    assert "epics:" in response.text


def test_set_yaml_preserves_order(client, ordered_yaml):
    file = BytesIO(ordered_yaml.encode("utf-8"))
    response = client.put(
        Endpoints.UPLOAD.with_prefix(), files={"file": ("test.yaml", file, "text/yaml")}
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
    from agileffp.yaml_editor.config import Endpoints

    app, _ = fast_app()
    build_api(app, None, None, prefix="/test")

    assert Endpoints.UPLOAD.with_prefix() == "/test" + Endpoints.UPLOAD.value
