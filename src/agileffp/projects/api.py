from dataclasses import dataclass
from datetime import datetime

from fasthtml.common import (
    APIRouter,
    DialogX,
    Div,
    FormData,
    P,
    Request,
    add_toast,
    database,
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


@dataclass
class ProjectDB:
    name: str
    description: str
    created_at: str


def init_db(app):
    db = database('data/projects.db')
    projects = db.create(ProjectDB, pk=('name', 'created_at'))
    return db, projects


def build_api(app, prefix: str = None):
    global _prefix
    _prefix = "/" + prefix.strip("/") if prefix else None

    router: APIRouter = APIRouter(prefix=prefix)
    db, projects = init_db(app)

    def render_projects():
        project_list = projects()
        return Grid(
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
                    cls="h-full"
                )
                for project in project_list
            ],
            Button(
                "New Project",
                UkIcon("plus"),
                hx_get=config.Endpoints.NEW_PROJECT.with_prefix(),
                hx_target="#new-project-dialog",
                hx_swap="innerHTML",
                cls="w-full"
            ),
            cols_md=1,
            cols_lg=2,
            cols_xl=3
        )

    @router.get(config.Endpoints.LIST.value)
    def list_projects():
        return render_projects()

    @router.get(config.Endpoints.NEW_PROJECT.value)
    def new_project_dialog():
        hdr = Div(
            P("New Project"),
            Button(
                UkIcon("x"),
                aria_label="Close",
                hx_get=config.Endpoints.NEW_PROJECT.with_prefix(),
                hx_target="#new-project-dialog",
                hx_swap="delete",
                cls=(ButtonT.ghost, "h-9 w-9 p-0"),
                style="width: 2.25rem;"
            ),
            cls="flex justify-between items-center px-4 py-1"
        )
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
            CardFooter(
                Button(
                    "Cancel",
                    hx_get=config.Endpoints.NEW_PROJECT.with_prefix(),
                    hx_target="#new-project-dialog",
                    hx_swap="delete"
                ),
                Button(
                    "Create",
                    hx_post=config.Endpoints.CREATE.with_prefix(),
                    hx_include="#new-project-dialog form",
                    hx_target="#projects-grid",
                    hx_swap="innerHTML"
                ),
                cls="flex justify-end space-x-2"
            ),
            header=hdr,
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

        project = ProjectDB(
            name=name,
            description=description,
            created_at=datetime.now().isoformat()
        )
        projects.insert(project)

        add_toast(request.session, "Project created successfully!", "success")
        return render_projects()

    @router.delete(config.Endpoints.DELETE.value)
    async def delete_project(request: Request):
        form: FormData = await request.form()
        name = form.get("name")

        if not name:
            add_toast(request.session, "Project name is required", "error")
            return

        projects.delete(name=name)
        add_toast(request.session, "Project deleted successfully!", "success")
        return render_projects()

    router.to_app(app)
