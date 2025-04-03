
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
    Card,
    CardBody,
    CardFooter,
    CardHeader,
    Grid,
    Input,
    Label,
    TextArea,
    UkIcon,
)

from agileffp.projects import config
from agileffp.projects.models.project import Project


def init_db(db: Database):
    config.PROJECTS_TABLE = db.create(Project, pk='name')


def build_api(app, db: Database, render_target: str, prefix: str = None):
    config.PREFIX = "/" + prefix.strip("/") if prefix else None
    config.RENDER_TARGET = render_target
    router: APIRouter = APIRouter(prefix=prefix)

    init_db(db)

    @router.get(config.Endpoints.LIST.value)
    def list_projects():
        return render_projects()

    @router.get(config.Endpoints.NEW_PROJECT.value)
    def new_project_dialog():
        hdr = P("New Project")

        ftr = CardFooter(
            Button(
                "Cancel",
                hx_get=config.Endpoints.NEW_PROJECT.with_prefix(),
                hx_target="#new-project-dialog",
                hx_swap="delete"
            ),
            Button(
                "Create",
                hx_post=config.Endpoints.CREATE.with_prefix(),
                hx_include="#new-project-dialog",
                hx_target=f"#{config.RENDER_TARGET}",
                hx_swap="innerHTML"
            ),
            cls="flex justify-end space-x-2"
        ),

        return DialogX(
            Div(
                Label("Name", for_="name"),
                Input(
                    id="name",
                    name="name",
                    required=True,
                    placeholder="Project name"
                ),
                Label("Description", for_="description"),
                TextArea(
                    id="description",
                    name="description",
                    required=True,
                    placeholder="Project description"
                ),
                cls="space-y-4"
            ),
            header=hdr,
            footer=ftr,
            open=True,
            id='new-project-dialog'
        )

    @router.post(config.Endpoints.CREATE.value)
    async def create_project(request: Request):
        form: FormData = await request.form()
        name = form.get("name")
        description = form.get("description")

        if not name or not description:
            add_toast(request.session,
                      "Name and description are required", "error")
            return

        project = Project(
            name=name,
            description=description,
        )
        config.PROJECTS_TABLE.insert(project)

        add_toast(request.session, "Project created successfully!", "success")
        return render_projects()

    @router.delete(config.Endpoints.DELETE.value)
    async def delete_project(request: Request):
        form: FormData = await request.form()
        name = form.get("name")

        if not name:
            add_toast(request.session, "Project name is required", "error")
            return

        config.PROJECTS_TABLE.delete(name=name)
        add_toast(request.session, "Project deleted successfully!", "success")
        return render_projects()

    router.to_app(app)


def render_projects():
    project_list = config.PROJECTS_TABLE()
    return (Grid(
        *[
            Card(
                CardHeader(
                    P(project.name),
                    Button(
                        UkIcon("trash"),
                        aria_label="Delete",
                        hx_delete=config.Endpoints.DELETE.with_prefix(),
                        hx_vals=f'{{"name": "{project.name}"}}',
                        cls=(ButtonT.ghost, "h-9 w-9 p-0"),
                        style="width: 2.25rem;"
                    ),
                    cls="flex justify-between items-center"
                ),
                CardBody(P(project.description)),
                cls="h-full",
                hx_get=f"{config.Endpoints.GET.with_prefix()}{project.name}",  # FIXME: endpoint not working
                hx_target=f"#{config.RENDER_TARGET}"
            )
            for project in project_list
        ],
        Button(
            "New Project",
            UkIcon("plus"),
            hx_get=config.Endpoints.NEW_PROJECT.with_prefix(),
            hx_target="#new-project-container",
            cls="w-full"
        ),
        cols_md=1,
        cols_lg=2,
        cols_xl=3
    ),
        Div(
        id="new-project-container",
    ))
