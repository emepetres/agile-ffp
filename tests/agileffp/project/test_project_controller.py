import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from fasthtml.common import fast_app, FormData

from agileffp.project.controller import list_projects, get_project_context, save_project_version
from tests.agileffp.mocks import MockProjectModel


@pytest.fixture
def mock_request():
    """Create a mock request with a session for testing."""
    request = MagicMock()
    request.session = {}
    request.headers = {"hx-current-url": "/project/test_project"}
    return request


@pytest.fixture
def mock_form():
    """Create a mock form data for testing."""
    form = MagicMock(spec=FormData)
    form.get = MagicMock(side_effect=lambda key, default=None: {
        "name": "test_project",
        "description": "Test Project",
        "yaml_content": "test: content",
        "version_name": "test-version",
        "version_date": "2023-01-01 12:00:00"
    }.get(key, default))
    return form


class TestProjectController:
    """Test the Project Controller functionality."""

    @patch('agileffp.project.controller.model')
    def test_list_projects(self, mock_model):
        # Set up a mock that returns test projects
        mock_model.get_projects.return_value = [
            MockProjectModel().create_project("project1", "Project 1"),
            MockProjectModel().create_project("project2", "Project 2")
        ]

        # Set up mock view
        with patch('agileffp.project.controller.view') as mock_view:
            mock_view.render_projects.return_value = "<div>Projects List</div>"

            # Call the function
            result = list_projects()

            # Verify the model was called to get projects
            mock_model.get_projects.assert_called_once()

            # Verify the view was called to render projects
            mock_view.render_projects.assert_called_once()

            # Verify the result
            assert result == "<div>Projects List</div>"

    @patch('agileffp.project.controller.model')
    def test_get_project_context(self, mock_model):
        # Set up the mock to return test data
        mock_model.get_yaml_version_context.return_value = (
            "version-1", "yaml content", "prev-version", "next-version"
        )

        # Call the function
        version, content, prev, next = get_project_context("test_project", "version-1")

        # Verify the model was called with the right parameters
        mock_model.get_yaml_version_context.assert_called_once_with("test_project", "version-1")

        # Verify the results
        assert version == "version-1"
        assert content == "yaml content"
        assert prev == "prev-version"
        assert next == "next-version"

    @patch('agileffp.project.controller.model')
    def test_save_project_version(self, mock_model):
        # Set up the mock
        mock_model.get_project.return_value = MockProjectModel().create_project(
            "test_project", "Test Project"
        )
        mock_model.create_yaml_version.return_value = MagicMock()

        # Test saving a version
        yaml_content = "test: content"
        version_name = "test-version"
        version_date = datetime(2023, 1, 1, 12, 0, 0)

        result = save_project_version("test_project", yaml_content, version_name, version_date)

        # Verify the model was called
        mock_model.get_project.assert_called_once_with("test_project")
        mock_model.create_yaml_version.assert_called_once_with(
            "test_project", version_name, yaml_content, version_date
        )

        # Verify the result
        assert result is True

        # Test with non-existent project
        mock_model.get_project.return_value = None

        result = save_project_version("nonexistent", yaml_content, version_name, version_date)

        # Verify the result
        assert result is False