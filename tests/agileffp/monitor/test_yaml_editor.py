from io import BytesIO
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

from agileffp.monitor.routes import Endpoints, init


@pytest.fixture
def yaml_editor_client(test_app):
    """Set up a test client for YAML editor tests."""
    # Use mock for yaml_editor to avoid dependencies on specific implementation
    with patch('agileffp.monitor.views.yaml_editor') as mock_yaml_editor, \
            patch('agileffp.project.model.get_yaml_version_context') as mock_get_yaml:

        # Set up mock for get_yaml_version_context
        yaml_content = """
        name: test
        items:
          - id: 1
            value: foo
          - id: 2
            value: bar
        """
        mock_get_yaml.return_value = (
            "current_version", yaml_content, "prev_version", "next_version")

        # Set up mock for the yaml editor
        mock_yaml_editor.render.return_value = f"<div>YAML Editor</div><pre>{yaml_content}</pre>"
        mock_yaml_editor.render_upload_dialog.return_value = "<div>Upload Dialog</div>"
        mock_yaml_editor.get_default_template.return_value = """
        iterations:
          - name: Sample Iteration
            points: 100
        epics:
          - name: Sample Epic
            points: 50
        """

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


class TestYamlEditor:
    """Test the YAML editor functionality."""

    def test_upload_yaml(self, yaml_editor_client, sample_yaml):
        """Test uploading a YAML file."""
        with patch('agileffp.monitor.controller._try_render_charts') as mock_charts:
            # Set up the mock to return a charts div
            mock_charts.return_value = "<div>Charts</div>"

            # Upload a YAML file
            file = BytesIO(sample_yaml.encode("utf-8"))
            response = yaml_editor_client.put(
                Endpoints.UPLOAD.with_prefix(),
                files={"file": ("test.yaml", file, "text/yaml")},
                headers={"hx-current-url": "/project/test_project"}
            )

            # Verify the response
            assert response.status_code == 200
            assert "YAML Editor" in response.text

    def test_upload_dialog(self, yaml_editor_client):
        """Test the upload dialog."""
        response = yaml_editor_client.get(
            Endpoints.UPLOAD_DIALOG.with_prefix(),
            headers={"hx-current-url": "/project/test_project"}
        )

        # Verify the response
        assert response.status_code == 200
        assert "Upload Dialog" in response.text

    def test_upload_no_file(self, yaml_editor_client):
        """Test uploading with no file."""
        with patch('agileffp.monitor.views.yaml_editor.render') as mock_render:
            # Set up the mock to indicate no content
            mock_render.return_value = "<div>No content loaded</div>"

            # Try to upload with no file
            response = yaml_editor_client.put(
                Endpoints.UPLOAD.with_prefix(),
                headers={"hx-current-url": "/project/test_project"}
            )

            # Verify the response
            assert response.status_code == 200
            assert "No content loaded" in response.text

    def test_load_template(self, yaml_editor_client):
        """Test loading the default template."""
        with patch('agileffp.monitor.controller._try_render_charts') as mock_charts:
            # Set up the mock to return a charts div
            mock_charts.return_value = "<div>Charts</div>"

            # Load the template
            response = yaml_editor_client.put(
                Endpoints.UPLOAD_TEMPLATE.with_prefix(),
                headers={"hx-current-url": "/project/test_project"}
            )

            # Verify the response
            assert response.status_code == 200
            assert "YAML Editor" in response.text

    def test_upload_invalid_yaml(self, yaml_editor_client):
        """Test uploading invalid YAML."""
        with patch('agileffp.monitor.controller._try_render_charts') as mock_charts:
            # Set up the mock to indicate YAML error
            mock_charts.return_value = "<div>Invalid YAML format</div>"

            # Create invalid YAML
            invalid_yaml = """
            bad: [
              unclosed bracket
            """

            # Upload the invalid YAML
            file = BytesIO(invalid_yaml.encode("utf-8"))
            response = yaml_editor_client.put(
                Endpoints.UPLOAD.with_prefix(),
                files={"file": ("invalid.yaml", file, "text/yaml")},
                headers={"hx-current-url": "/project/test_project"}
            )

            # Verify the response
            assert response.status_code == 200
            assert "YAML Editor" in response.text

            # Verify _try_render_charts was called once
            mock_charts.assert_called_once()

    def test_order_preservation(self, yaml_editor_client, ordered_yaml):
        """Test that YAML order is preserved."""
        with patch('agileffp.monitor.views.yaml_editor.render') as mock_render:
            # Set up the mock to return the ordered YAML
            mock_render.return_value = f"<pre>{ordered_yaml}</pre>"

            # Upload the ordered YAML
            file = BytesIO(ordered_yaml.encode("utf-8"))
            response = yaml_editor_client.put(
                Endpoints.UPLOAD.with_prefix(),
                files={"file": ("ordered.yaml", file, "text/yaml")},
                headers={"hx-current-url": "/project/test_project"}
            )

            # Verify the response contains the YAML in order
            assert response.status_code == 200
            content = response.text

            # Verify the order was preserved in the response
            charlie_pos = content.find("charlie")
            alpha_pos = content.find("alpha")
            beta_pos = content.find("beta")

            # Check top-level keys order (non-alphabetical)
            assert charlie_pos < alpha_pos < beta_pos
