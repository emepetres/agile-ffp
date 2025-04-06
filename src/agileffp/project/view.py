from fasthtml.common import (
    DialogX,
    Div,
    P,
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

from agileffp.project import model, routes


def render_projects(projects: list[model.Project], render_target: str):
    return (Grid(
        *[
            Card(
                CardHeader(
                    P(project.name),
                    Button(
                        UkIcon("trash"),
                        aria_label="Delete",
                        hx_delete=routes.Endpoints.DELETE.with_prefix(),
                        hx_vals=f'{{"name": "{project.name}"}}',
                        cls=(ButtonT.ghost, "h-9 w-9 p-0"),
                        style="width: 2.25rem;"
                    ),
                    cls="flex justify-between items-center"
                ),
                CardBody(P(project.description)),
                cls="h-full",
                hx_get=f"{routes.Endpoints.GET.with_prefix()}{project.name}",
                hx_target=f"#{render_target}"
            )
            for project in projects
        ],
        Button(
            "New Project",
            UkIcon("plus"),
            hx_get=routes.Endpoints.NEW_PROJECT.with_prefix(),
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


def render_new_project_dialog(render_target: str):
    hdr = P("New Project")

    ftr = CardFooter(
        Button(
            "Cancel",
            hx_get=routes.Endpoints.NEW_PROJECT.with_prefix(),
            hx_target="#new-project-dialog",
            hx_swap="delete"
        ),
        Button(
            "Create",
            hx_post=routes.Endpoints.CREATE.with_prefix(),
            hx_include="#new-project-dialog",
            hx_target=f"#{render_target}",
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
