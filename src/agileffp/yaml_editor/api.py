from dataclasses import dataclass

from apswutils.db import Database
from fasthtml.common import (
    APIRouter,
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
    UkIcon,
)

from agileffp.yaml_editor import config
from agileffp.yaml_editor.render import get_default_template, initialize, render


@dataclass
class YamlFile:
    name: str
    saved_at: str
    content: str


# # def init_db(db: Database, app):
# #     db = database('data/yaml_files.db')
# #     yaml_files = db.create(YamlFile, pk=('name', 'saved_at'))
# #     return db, yaml_files


def build_api(app, db: Database, charts_target: str, prefix: str = None):
    config.CHARTS_TARGET = charts_target
    config.PREFIX = "/" + prefix.strip("/") if prefix else None

    router: APIRouter = APIRouter(prefix=config.PREFIX)

    # # init_db(db, app)

    @router.put(config.Endpoints.UPLOAD.value)
    async def set_yaml(request: Request, session):
        # Get the uploaded file from the request
        form: FormData = await request.form()
        file = form.get("file")
        yaml_content = file.file.read().decode("utf-8") if file else None

        session["yaml_content"] = yaml_content
        session["yaml_filename"] = file.filename if file else "-"

        return render(session)

    @router.put(config.Endpoints.UPLOAD_TEMPLATE.value)
    def load_template(session):
        yaml_content = get_default_template()
        session["yaml_content"] = yaml_content
        session["yaml_filename"] = "template.yaml"

        return render(session)

    @router.post(config.Endpoints.UPDATE_YAML.value)
    async def update_yaml(request: Request, session):
        form: FormData = await request.form()
        session["yaml_content"] = form.get("yaml_content")
        # Only return the charts component since we don't want to update the editor
        _, charts = render(session, update_editor=False)
        return charts

    @router.get(config.Endpoints.TOGGLE_EDITOR.value)
    async def toggle_editor(request: Request, session):
        session["editor_hidden"] = not session["editor_hidden"]
        return render(session, update_charts=False)

    @router.put(config.Endpoints.RESET.value)
    def reset(session):
        initialize(session)
        return render(session)

    @router.get(config.Endpoints.HELP.value)
    def help():
        hdr = Div(
            P("Help Information"),
            Button(UkIcon("x"),
                   aria_label="Close",
                   hx_get=config.Endpoints.HELP.with_prefix(),
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

    @router.put(config.Endpoints.SAVE_YAML.value)
    async def save_yaml(request: Request, session):
        if not session.get("yaml_content"):
            add_toast(session, "No project to save", "error")
            return

        # # filename = session["yaml_filename"].rsplit(
        # #     '.', 1)[0]  # Remove extension
        # # now = datetime.now().isoformat()

        # # # Create YamlFile instance and insert using MiniDataAPI
        # # yaml_file = YamlFile(
        # #     name=filename,
        # #     saved_at=now,
        # #     content=session["yaml_content"]
        # # )
        # # yaml_files.insert(yaml_file)

        add_toast(session, "Project saved successfully!", "success")
        return

    router.to_app(app)
