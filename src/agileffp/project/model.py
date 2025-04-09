from apswutils.db import Database
from fasthtml.common import NotFoundError
from pydantic import BaseModel


class Project(BaseModel):
    name: str
    description: str
    yaml_content: str

    # needed for db persistence
    def __init__(self, name: str, description: str, yaml_content: str = "") -> None:
        super().__init__(name=name, description=description, yaml_content=yaml_content)


_projects_table = None


def init(db: Database):
    global _projects_table
    _projects_table = db.create(Project, pk='name', transform=True)


def get_projects():
    return _projects_table()


def create_project(name: str, description: str, yaml_content: str = ""):
    _projects_table.insert(Project(name, description, yaml_content))


def delete_project(name: str):
    _projects_table.delete(name=name)


def get_project(name: str):
    try:
        return _projects_table[name]
    except NotFoundError:
        return None


def update_project(name: str, yaml_content: str) -> bool:
    project = get_project(name)
    if project:
        project.yaml_content = yaml_content
        _projects_table.update(project)
        return True
    return False
