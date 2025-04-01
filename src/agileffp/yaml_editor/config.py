from enum import Enum

CHARTS_TARGET: str = None
PREFIX: str = None


class Endpoints(Enum):
    UPLOAD = "/upload"
    UPLOAD_TEMPLATE = "/upload_template"
    TOGGLE_EDITOR = "/toggle_editor"
    UPDATE_YAML = "/update_yaml"
    RESET = "/reset"
    HELP = "/help"
    SAVE_YAML = "/save_yaml"

    def with_prefix(self) -> str:
        if not PREFIX:
            return self.value

        return f"{PREFIX}{self.value}"
