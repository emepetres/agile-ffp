from datetime import datetime
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel


class MockYamlVersion(BaseModel):
    project_name: str
    name: str
    date: datetime
    yaml_content: str


class MockProject(BaseModel):
    name: str
    description: str


class MockProjectModel:
    """Mock implementation of the project model for testing."""

    def __init__(self):
        self.projects: Dict[str, MockProject] = {}
        self.versions: Dict[str, List[MockYamlVersion]] = {}

        # Add a default test project
        self.create_project("test_project", "Test Project Description")

        # Add default template content
        self.default_template = """
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
        # Create a version for the test project
        self.create_yaml_version("test_project", "version-1", self.default_template)

    def get_projects(self) -> List[MockProject]:
        return list(self.projects.values())

    def create_project(self, name: str, description: str) -> MockProject:
        project = MockProject(name=name, description=description)
        self.projects[name] = project
        self.versions[name] = []
        return project

    def delete_project(self, name: str) -> bool:
        if name in self.projects:
            del self.projects[name]
            if name in self.versions:
                del self.versions[name]
            return True
        return False

    def get_project(self, name: str) -> Optional[MockProject]:
        return self.projects.get(name)

    def create_yaml_version(self, project_name: str, name: str, yaml_content: str,
                            date: datetime = None) -> MockYamlVersion:
        if date is None:
            date = datetime.now()

        version = MockYamlVersion(
            project_name=project_name,
            name=name,
            date=date,
            yaml_content=yaml_content
        )

        if project_name not in self.versions:
            self.versions[project_name] = []

        self.versions[project_name].append(version)
        return version

    def get_yaml_version_context(self, project_name: str, version_name: str = None) -> Tuple:
        if project_name not in self.versions or not self.versions[project_name]:
            return None, None, None, None

        versions = self.versions[project_name]

        if version_name:
            # Find the specified version
            version_index = next((i for i, v in enumerate(versions)
                                if v.name == version_name), len(versions) - 1)
        else:
            # Default to the latest version
            version_index = len(versions) - 1

        version = versions[version_index]
        prev_version = versions[version_index - 1].name if version_index > 0 else None
        next_version = (versions[version_index + 1].name
                        if version_index < len(versions) - 1 else None)

        return version.name, version.yaml_content, prev_version, next_version

    def delete_yaml_version(self, project_name: str, version_name: str) -> bool:
        if project_name not in self.versions:
            return False

        initial_count = len(self.versions[project_name])
        self.versions[project_name] = [v for v in self.versions[project_name]
                                     if v.name != version_name]

        return len(self.versions[project_name]) < initial_count


class MockYamlEditor:
    """Mock implementation of the YAML editor functionality."""

    def __init__(self):
        self.default_template = """
iterations:
  - name: Sample Iteration
    points: 100
epics:
  - name: Sample Epic
    points: 50
"""

    def get_default_template(self):
        return self.default_template

    def render(self, hide: bool, version: str, yaml_content: str,
               prev_version, next_version, charts_target: str):
        if hide:
            return "<div>YAML Editor (Hidden)</div>"

        # Simple HTML representation for testing
        html = f"<div>YAML Editor: version={version}</div>"

        if yaml_content:
            html += f"<pre>{yaml_content}</pre>"

        return html

    def render_controls(self, version, prev_version, next_version):
        return f"<div>Controls: version={version}</div>"

    def render_upload_dialog(self):
        return "<div>Upload YAML Dialog</div>"

    def render_save_version_dialog(self, yaml_content):
        return "<div>Save Version Dialog</div>"

    def render_help_dialog(self):
        return "<div>Help Dialog</div>"