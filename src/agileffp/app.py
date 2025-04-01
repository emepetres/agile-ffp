from apswutils.db import Database
from fasthtml.common import (
    Container,
    Img,
    Script,
    Titled,
    database,
    fast_app,
    serve,
    setup_toasts,
)
from monsterui.all import (
    DivHStacked,
    DivVStacked,
    Theme,
)

from agileffp.constants import (
    CHARTS_CONTAINER_ID,
    DB_PATH,
    EDITOR_API_PREFIX,
    PROJECTS_API_PREFIX,
)
from agileffp.projects.api import build_api as build_projects_api
from agileffp.projects.api import render_projects
from agileffp.yaml_editor.api import build_api as build_editor_api
from agileffp.yaml_editor.render import initialize as render_editor

headers = (
    Theme.blue.headers(),
    Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"),
    Script(src="https://cdn.plot.ly/plotly-2.24.1.min.js"),
)

db: Database = database(DB_PATH)
app, rt = fast_app(hdrs=headers, static_path="static")
setup_toasts(app)
build_projects_api(app, db, CHARTS_CONTAINER_ID, prefix=PROJECTS_API_PREFIX)
build_editor_api(app, db, CHARTS_CONTAINER_ID, prefix=EDITOR_API_PREFIX)


@rt("/")
def index(session):
    return Titled(
        "AgileFFP - by Javier Carnero",
        Container(
            DivHStacked(
                DivVStacked(
                    render_projects(),
                    id=CHARTS_CONTAINER_ID,
                    hx_swap_oob="true",
                    cls="container mt-8 mx-auto",
                ),
                render_editor(session),
                cls="gap-4",
            ),
        ),
        Img(
            id="spinner",
            cls="htmx-indicator fixed inset-0 m-auto",
            src="images/loading-spinner.svg",
            alt="Computing charts...",
        ),
    )


if __name__ == "__main__":
    print("----Development environment----")

    serve(appname="agileffp.app", app="app", reload=True)
