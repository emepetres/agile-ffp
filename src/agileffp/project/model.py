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
    yaml_content: str

    # needed for db persistence
    def __init__(self, name: str, description: str, yaml_content: str = "") -> None:
        super().__init__(name=name, description=description, yaml_content=yaml_content)


_projects_table = None
_yaml_versions_table = None


def init(db: Database):
    global _projects_table, _yaml_versions_table
    _projects_table = db.create(Project, pk='name', transform=True)
    _yaml_versions_table = db.create(YamlVersion, pk=['project_name', 'name'], transform=True)


def get_projects():
    return _projects_table()


def create_project(name: str, description: str, yaml_content: str = ""):
    _projects_table.insert(Project(name, description, yaml_content))


def delete_project(name: str):
    _projects_table.delete(name=name)
    # Delete all versions associated with this project
    for version in get_yaml_versions(name):
        _yaml_versions_table.delete(id=version.id)


def get_project(name: str):
    try:
        project = _projects_table[name]
        # Get the latest version if it exists
        latest_version = get_latest_yaml_version(name)
        if latest_version:
            project.yaml_content = latest_version.yaml_content
        return project
    except NotFoundError:
        return None


def update_project(name: str, yaml_content: str) -> bool:
    project = get_project(name)
    if project:
        # Store the current version in the project for backward compatibility
        project.yaml_content = yaml_content
        _projects_table.update(project)

        # Create a new version with random name and current datetime
        create_yaml_version(
            name, f"Version-{uuid.uuid4().hex[:8]}", yaml_content)
        return True
    return False


def create_yaml_version(project_name: str, name: str, yaml_content: str):
    version = YamlVersion(project_name, name, datetime.now(), yaml_content)
    _yaml_versions_table.insert(version)
    return version


def get_yaml_versions(project_name: str):
    return [v for v in _yaml_versions_table() if v.project_name == project_name]


def get_latest_yaml_version(project_name: str):
    versions = get_yaml_versions(project_name)
    if not versions:
        return None
    return max(versions, key=lambda v: v.date)
