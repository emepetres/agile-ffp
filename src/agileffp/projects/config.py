from enum import Enum

PREFIX: str = None


class Endpoints(Enum):
    LIST = "/list"
    CREATE = "/create"
    DELETE = "/delete"
    NEW_PROJECT = "/new_project"

    def with_prefix(self) -> str:
        if not PREFIX:
            return self.value
        return f"{PREFIX}{self.value}"
