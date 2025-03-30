from fasthtml.common import (
    Container,
    Img,
    Script,
    Titled,
    fast_app,
    serve,
    setup_toasts,
)
from monsterui.all import (
    DivHStacked,
    Theme,
)

from agileffp import yaml_editor
from agileffp.roadmap import charts

headers = (
    Theme.blue.headers(),
    Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"),
    Script(src="https://cdn.plot.ly/plotly-2.24.1.min.js"),
)

charts_id = "main-content"
app, rt = fast_app(hdrs=headers, static_path="static")
setup_toasts(app)
yaml_editor.build_api(app, charts_id, prefix="/editor")


@rt("/")
def index(session):
    return Titled(
        "AgileFFP - by Javier Carnero",
        Container(
            DivHStacked(
                # Main content (spans all width)
                charts.initialize(charts_id),
                # Right content (spans 1/3 width)
                yaml_editor.initialize(session),
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
