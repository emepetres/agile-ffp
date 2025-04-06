from apswutils.db import Database
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
    _projects_table = db.create(Project, pk='name')


def get_projects():
    return _projects_table()


def create_project(name: str, description: str, yaml_content: str = ""):
    _projects_table.insert(Project(name, description, yaml_content))


def delete_project(name: str):
    _projects_table.delete(name=name)


def get_project(name: str):
    return _projects_table.get(name=name)
