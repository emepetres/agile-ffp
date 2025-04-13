from enum import Enum

from fasthtml.common import (
    APIRouter,
)

from agileffp.monitor import controller

_prefix: str = None


class Endpoints(Enum):
    TOGGLE_EDITOR = "/toggle_editor"
    UPLOAD_DIALOG = "/upload_dialog"
    SAVE_VERSION_DIALOG = "/save_version_dialog"
    UPLOAD = "/upload"
    UPLOAD_TEMPLATE = "/load_template"
    UPDATE_YAML = "/update_yaml"
    SAVE_YAML = "/save_yaml"
    DOWNLOAD_YAML = "/download_yaml"
    HELP = "/help"
    VERSION = "/version"

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
