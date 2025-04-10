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

    @router.put(endpoints.SAVE_YAML.value)
    async def save_yaml(request: Request, session):
        form: FormData = await request.form()
        session["yaml_content"] = form.get("yaml_content")
        if not session["yaml_content"]:
            add_toast(session, "No yaml content to save", "error")
            return

        success = project_controller.update_project(
            session["project_name"], session["yaml_content"])

        if success:
            add_toast(
                session, "Project saved successfully! New version created.", "success")
        else:
            add_toast(session, "Failed to save project", "error")
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
