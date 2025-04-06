from enum import Enum

from apswutils.db import Database
from fasthtml.common import (
    APIRouter,
)

from agileffp.project import controller, model

_prefix: str = None


class Endpoints(Enum):
    LIST = "/list"
    CREATE = "/create"
    DELETE = "/delete"
    NEW_PROJECT = "/new_project"
    GET = "/"

    def with_prefix(self) -> str:
        if not _prefix:
            return self.value
        return f"{_prefix}{self.value}"


def init(app, db: Database, render_target: str, prefix: str = None) -> APIRouter:
    global _prefix
    _prefix = "/" + prefix.strip("/") if prefix else None

    model.init(db)
    router = APIRouter(prefix=_prefix)
    controller.init(router, Endpoints, render_target)
    router.to_app(app)
