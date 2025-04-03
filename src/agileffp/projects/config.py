from enum import Enum

RENDER_TARGET: str = None
PREFIX: str = None
PROJECTS_TABLE = None


class Endpoints(Enum):
    LIST = "/list"
    CREATE = "/create"
    DELETE = "/delete"
    NEW_PROJECT = "/new_project"
    GET = "/"

    def with_prefix(self) -> str:
        if not PREFIX:
            return self.value
        return f"{PREFIX}{self.value}"
