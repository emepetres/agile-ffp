import uuid
from datetime import datetime

from apswutils.db import Database
from fasthtml.common import NotFoundError
from pydantic import BaseModel


class YamlVersion(BaseModel):
    project_name: str
    name: str
    date: datetime
    yaml_content: str

    # needed for db persistence
    def __init__(self, project_name: str, name: str, date: datetime, yaml_content: str) -> None:
        super().__init__(project_name=project_name,
                         name=name, date=date, yaml_content=yaml_content)


class Project(BaseModel):
    name: str
    description: str

    # needed for db persistence
    def __init__(self, name: str, description: str) -> None:
        super().__init__(name=name, description=description)


_projects_table = None
_yaml_versions_table = None


def init(db: Database):
    global _projects_table, _yaml_versions_table
    _projects_table = db.create(Project, pk='name', transform=True)
    _yaml_versions_table = db.create(
        YamlVersion, pk=['project_name', 'name'], transform=True)


def get_projects():
    return _projects_table()


def create_project(name: str, description: str):
    _projects_table.insert(Project(name, description))


def delete_project(name: str):
    _projects_table.delete(name=name)
    # Delete all versions associated with this project
    for version in _get_yaml_versions(name):
        _yaml_versions_table.delete(
            project_name=version.project_name, name=version.name)


def get_project(name: str):
    try:
        return _projects_table[name]
    except NotFoundError:
        return None


def update_project(name: str, yaml_content: str) -> bool:
    """Update project and create a version with auto-generated name"""
    return update_project_content(name, yaml_content) and \
        create_yaml_version(
            name, f"Version-{uuid.uuid4().hex[:8]}", yaml_content) is not None


def update_project_content(name: str, yaml_content: str) -> bool:
    """Update only the project's yaml_content without creating a version"""
    project = get_project(name)
    if project:
        # Store the current version in the project for backward compatibility
        project.yaml_content = yaml_content
        _projects_table.update(project)
        return True
    return False


def create_yaml_version(project_name: str, name: str, yaml_content: str, date: datetime = None) -> YamlVersion:
    """Create a new version with provided name and date (or current date)"""
    if date is None:
        date = datetime.now()

    version = YamlVersion(project_name, name, date, yaml_content)
    _yaml_versions_table.insert(version)
    return version


def get_yaml_version_context(project_name: str, version_name: str = None):
    versions = _get_yaml_versions(project_name)
    if not versions:
        return None, None, None, None

    vnames = [v.name for v in versions]
    version_index = len(versions) - 1
    if version_name:
        version_index = vnames.index(version_name)

    version = versions[version_index].name
    yaml_content = versions[version_index].yaml_content
    prev_version = versions[version_index - 1].name if version_index > 0 else None
    next_version = versions[version_index +
                            1].name if version_index < len(versions) - 1 else None

    return version, yaml_content, prev_version, next_version


def _get_yaml_versions(project_name: str):
    return _yaml_versions_table("project_name=?", (project_name,), order_by="date")


def _get_yaml_version(project_name: str, version_name: str):
    try:
        return _yaml_versions_table[project_name, version_name]
    except NotFoundError:
        return None
