from enum import Enum

from fasthtml.common import (
    APIRouter,
)

from agileffp.monitor import controller

_prefix: str = None


class Endpoints(Enum):
    UPLOAD = "/upload"
    UPLOAD_TEMPLATE = "/upload_template"
    TOGGLE_EDITOR = "/toggle_editor"
    UPDATE_YAML = "/update_yaml"
    RESET = "/reset"
    HELP = "/help"
    SAVE_YAML = "/save_yaml"

    def with_prefix(self) -> str:
        if not _prefix:
            return self.value

        return f"{_prefix}{self.value}"


def init(app, charts_target: str, prefix: str = None) -> APIRouter:
    global _prefix
    _prefix = "/" + prefix.strip("/") if prefix else None

    router = APIRouter(prefix=_prefix)
    controller.init(router, Endpoints, charts_target)
    router.to_app(app)
