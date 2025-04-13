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
        version = "dirty"
        prev_version = None
        next_version = None
        form: FormData = await request.form()
        file = form.get("file")
        yaml_content = file.file.read().decode("utf-8") if file else None

        return (yaml_editor.render(session["editor_hidden"], version, yaml_content, prev_version, next_version, _charts_target), _try_render_charts(yaml_content))

    @router.put(endpoints.UPLOAD_TEMPLATE.value)
    def load_template():
        version = "dirty"
        prev_version = None
        next_version = None
        yaml_content = yaml_editor.get_default_template()

        return (yaml_editor.render(False, version, yaml_content, prev_version, next_version, _charts_target), _try_render_charts(yaml_content))

    @router.post(endpoints.UPDATE_YAML.value)
    async def update_yaml(request: Request):
        form: FormData = await request.form()
        yaml_content = form.get("yaml_content")

        # TODO: we should update the version to "dirty", without refreshing content

        return _try_render_charts(yaml_content)

    @router.get(endpoints.TOGGLE_EDITOR.value)
    async def toggle_editor(hide: bool, version: str, request: Request):
        if not hide:
            project_name = request.headers.get("hx-current-url").split("/")[-1]
            version, yaml_content, prev_version, next_version = project_controller.get_project_context(
                project_name, version)
        else:
            version = ""
            prev_version = None
            next_version = None
            yaml_content = None

        return yaml_editor.render(hide, version, yaml_content, prev_version, next_version, _charts_target)

    @router.get(endpoints.HELP.value)
    def help():
        return yaml_editor.render_help_dialog()

    @router.get(endpoints.VERSION.value)
    def version(version: str, request: Request):
        project_name = request.headers.get("hx-current-url").split("/")[-1]
        version, yaml_content, prev_version, next_version = project_controller.get_project_context(
            project_name, version)
        return (
            yaml_editor.render(False, version, yaml_content,
                               prev_version, next_version, _charts_target),
            _try_render_charts(yaml_content))

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
            session["current_version_name"] = version_name

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


def index(name: str):
    version, yaml_content, prev_version, next_version = project_controller.get_project_context(
        name)
    return (
        _try_render_charts(yaml_content, swap=False),
        yaml_editor.render(False, version, yaml_content, prev_version, next_version, _charts_target))


def _try_render_charts(yaml_content: str, swap: bool = True):
    _charts = None
    try:
        yaml_data = yaml.safe_load(yaml_content) if yaml_content else None
        _charts = charts.render_charts(yaml_data, _charts_target, swap)
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
