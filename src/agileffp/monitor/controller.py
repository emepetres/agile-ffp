from datetime import datetime

import yaml
from fasthtml.common import (
    Div,
    FormData,
    Request,
    StreamingResponse,
    add_toast,
)
from monsterui.all import (
    TextT,
)

from agileffp.monitor.views import charts, yaml_editor
from agileffp.project import controller as project_controller

_charts_target = None


def init(router, endpoints, charts_target: str):
    global _charts_target
    _charts_target = charts_target

    @router.get(endpoints.UPLOAD_DIALOG.value)
    def upload_dialog():
        return yaml_editor.render_upload_dialog()

    @router.get(endpoints.SAVE_VERSION_DIALOG.value)
    async def save_version_dialog(request: Request):
        form: FormData = await request.form()
        yaml_content = form.get("yaml_content", "")
        return yaml_editor.render_save_version_dialog(yaml_content)

    @router.put(endpoints.UPLOAD.value)
    async def upload_yaml(request: Request, session):
        # Get the uploaded file from the request
        form: FormData = await request.form()
        file = form.get("file")
        yaml_content = file.file.read().decode("utf-8") if file else None

        session["yaml_content"] = yaml_content

        return yaml_editor.render(session["editor_hidden"], yaml_content, _charts_target), _try_render_charts(session)

    @router.put(endpoints.UPLOAD_TEMPLATE.value)
    def load_template(session):
        yaml_content = yaml_editor.get_default_template()
        session["yaml_content"] = yaml_content

        return yaml_editor.render(session["editor_hidden"], yaml_content, _charts_target), _try_render_charts(session)

    @router.post(endpoints.UPDATE_YAML.value)
    async def update_yaml(request: Request, session):
        form: FormData = await request.form()
        session["yaml_content"] = form.get("yaml_content")
        # we don't want to update the editor
        return _try_render_charts(session)

    @router.get(endpoints.TOGGLE_EDITOR.value)
    async def toggle_editor(request: Request, session):
        session["editor_hidden"] = not session["editor_hidden"]
        return yaml_editor.render(session["editor_hidden"], session["yaml_content"], _charts_target)

    @router.get(endpoints.HELP.value)
    def help():
        return yaml_editor.render_help_dialog()

    @router.post(endpoints.SAVE_YAML.value)
    async def save_yaml(request: Request, session):
        form: FormData = await request.form()
        yaml_content = form.get("yaml_content")
        version_name = form.get("version_name")
        version_date_str = form.get("version_date")

        if not yaml_content:
            add_toast(session, "No yaml content to save", "error")
            return

        if not version_name:
            version_name = f"Version-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        try:
            # Parse the date string
            if version_date_str:
                version_date = datetime.strptime(
                    version_date_str, "%Y-%m-%d %H:%M:%S")
            else:
                version_date = datetime.now()

            # Update session yaml content
            session["yaml_content"] = yaml_content

            # Call the project controller to save with version info
            success = project_controller.save_project_version(
                session["project_name"], yaml_content, version_name, version_date)

            if success:
                add_toast(
                    session, f"Project saved as version '{version_name}'", "success")
            else:
                add_toast(session, "Failed to save project version", "error")

        except ValueError:
            add_toast(
                session, "Invalid date format. Please use YYYY-MM-DD HH:MM:SS", "error")

        return

    @router.put(endpoints.DOWNLOAD_YAML.value)
    async def export_yaml(request: Request, session):
        form: FormData = await request.form()
        yaml_content = form.get("yaml_content")

        if not yaml_content:
            add_toast(session, "No yaml content to export", "error")
            return

        # Create an async generator to stream the content
        async def content_generator():
            yield yaml_content.encode()

        return StreamingResponse(
            content_generator(),
            media_type="application/yaml",
            headers={
                "Content-Disposition": "attachment; filename=project.yaml",
                "HX-Trigger": "fileDownload"
            }
        )


def index(session, name, yaml_content):
    session["project_name"] = name
    session["yaml_content"] = yaml_content
    session["editor_hidden"] = False

    return (
        _try_render_charts(session, swap=False),
        yaml_editor.render(session["editor_hidden"], yaml_content, _charts_target))


def _try_render_charts(session, swap: bool = True):
    _charts = None
    try:
        yaml_data = yaml.safe_load(
            session["yaml_content"]) if session["yaml_content"] else None
        _charts = charts.render_charts(
            yaml_data, _charts_target, swap) if yaml_data else None
    except yaml.YAMLError as e:
        _charts = Div(
            f"Invalid YAML format: {str(e)}", cls=TextT.error, id=_charts_target)
        if swap:
            _charts.hx_swap_oob = 'true'
    except Exception as e:
        _charts = Div(
            f"Error processing YAML: {str(e)}", cls=TextT.error, id=_charts_target)
        if swap:
            _charts.hx_swap_oob = 'true'

    return _charts
