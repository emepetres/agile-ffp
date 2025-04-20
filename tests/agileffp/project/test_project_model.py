import pytest
from datetime import datetime

from tests.agileffp.mocks import MockProjectModel


class TestProjectModel:
    """Test the Project Model functionality."""

    def test_create_project(self, mock_project_model):
        # Test creating a new project
        project = mock_project_model.create_project("new_project", "New Project Description")

        assert project.name == "new_project"
        assert project.description == "New Project Description"
        assert "new_project" in mock_project_model.projects
        assert "new_project" in mock_project_model.versions

    def test_get_projects(self, mock_project_model):
        # Create some test projects
        mock_project_model.create_project("project1", "Project 1")
        mock_project_model.create_project("project2", "Project 2")

        # Get all projects
        projects = mock_project_model.get_projects()

        # Verify the projects are returned
        project_names = [p.name for p in projects]
        assert "test_project" in project_names
        assert "project1" in project_names
        assert "project2" in project_names

    def test_get_project(self, mock_project_model):
        # Test getting an existing project
        project = mock_project_model.get_project("test_project")
        assert project is not None
        assert project.name == "test_project"

        # Test getting a non-existent project
        project = mock_project_model.get_project("nonexistent")
        assert project is None

    def test_delete_project(self, mock_project_model):
        # Create a project to delete
        mock_project_model.create_project("to_delete", "Project to Delete")

        # Verify it exists
        assert "to_delete" in mock_project_model.projects

        # Delete the project
        result = mock_project_model.delete_project("to_delete")

        # Verify it was deleted
        assert result is True
        assert "to_delete" not in mock_project_model.projects

        # Try to delete a non-existent project
        result = mock_project_model.delete_project("nonexistent")
        assert result is False

    def test_create_yaml_version(self, mock_project_model):
        # Test creating a version
        yaml_content = "test: content"
        date = datetime(2023, 1, 1, 12, 0, 0)

        version = mock_project_model.create_yaml_version(
            "test_project", "new-version", yaml_content, date
        )

        assert version.project_name == "test_project"
        assert version.name == "new-version"
        assert version.yaml_content == yaml_content
        assert version.date == date

        # Check that the version was added to the project
        assert version in mock_project_model.versions["test_project"]

    def test_get_yaml_version_context(self, mock_project_model):
        # Create multiple versions for a project
        mock_project_model.create_yaml_version(
            "test_project", "v1", "content1", datetime(2023, 1, 1)
        )
        mock_project_model.create_yaml_version(
            "test_project", "v2", "content2", datetime(2023, 1, 2)
        )
        mock_project_model.create_yaml_version(
            "test_project", "v3", "content3", datetime(2023, 1, 3)
        )

        # Test getting a specific version
        version, content, prev, next = mock_project_model.get_yaml_version_context(
            "test_project", "v2"
        )

        assert version == "v2"
        assert content == "content2"
        assert prev == "v1"
        assert next == "v3"

        # Test getting the latest version (default)
        version, content, prev, next = mock_project_model.get_yaml_version_context(
            "test_project"
        )

        assert version == "v3"
        assert content == "content3"
        assert prev == "v2"
        assert next is None

    def test_delete_yaml_version(self, mock_project_model):
        # Create versions to delete
        mock_project_model.create_yaml_version(
            "test_project", "to_delete", "content", datetime(2023, 1, 1)
        )

        # Verify we can delete it
        result = mock_project_model.delete_yaml_version("test_project", "to_delete")
        assert result is True

        # Verify it's not in the versions anymore
        versions = mock_project_model.versions["test_project"]
        version_names = [v.name for v in versions]
        assert "to_delete" not in version_names

        # Try to delete a non-existent version
        result = mock_project_model.delete_yaml_version("test_project", "nonexistent")
        assert result is False

        # Try to delete from a non-existent project
        result = mock_project_model.delete_yaml_version("nonexistent", "any")
        assert result is False