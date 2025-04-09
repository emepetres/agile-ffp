import yaml
from fasthtml.common import (
    DialogX,
    Div,
    FormData,
    P,
    Request,
    add_toast,
)
from monsterui.all import (
    Button,
    ButtonT,
    TextT,
    UkIcon,
)

from agileffp.monitor.views import charts, yaml_editor
from agileffp.project import controller as project_controller

_charts_target = None


def init(router, endpoints, charts_target: str):
    global _charts_target
    _charts_target = charts_target

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

    # # @router.put(endpoints.RESET.value)
    # # def reset(session):
    # #     initialize(session)
    # #     return yaml_editor.render(session["editor_hidden"], session["yaml_content"], _charts_target), _try_render_charts(session)

    @router.get(endpoints.HELP.value)
    def help():
        hdr = Div(
            P("Help Information"),
            Button(UkIcon("x"),
                   aria_label="Close",
                   hx_get=endpoints.HELP.with_prefix(),
                   hx_target="#help-dialog",
                   hx_swap="delete",
                   cls=(ButtonT.ghost, "h-9 w-9 p-0"),
                   style="width: 2.25rem;"
                   ),
            cls="flex justify-between items-center px-4 py-1"
        )
        return DialogX(
            P("Here is some helpful information about using the YAML editor."),
            header=hdr,
            open=True,
            id='help-dialog'
        )

    @router.put(endpoints.SAVE_YAML.value)
    async def save_yaml(request: Request, session):
        form: FormData = await request.form()
        session["yaml_content"] = form.get("yaml_content")
        if not session.get("yaml_content"):
            add_toast(session, "No yaml content to save", "error")
            return

        project_controller.update_project(
            session["project_name"], session["yaml_content"])

        add_toast(session, "Project saved successfully!", "success")
        return


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
            f"Invalid YAML format: {str(e)}", cls=TextT.error, hx_swap_oob=swap, id=_charts_target)
    except Exception as e:
        _charts = Div(
            f"Error processing YAML: {str(e)}", cls=TextT.error, hx_swap_oob=swap, id=_charts_target)

    return _charts
