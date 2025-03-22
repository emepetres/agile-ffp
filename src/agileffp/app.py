from fasthtml.common import (
    H2,
    Container,
    Div,
    P,
    Script,
    Titled,
    fast_app,
    serve,
)
from monsterui.all import (
    DivHStacked,
    Theme,
)

from agileffp import yaml_editor

headers = (
    Theme.blue.headers(),
    Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"),
    Script(src="https://cdn.plot.ly/plotly-2.24.1.min.js"),
)

charts_id = "main-content"
app, rt = fast_app(hdrs=headers)
yaml_editor.build_api(app, charts_id, prefix="/editor")


@rt("/")
def index(session):
    return Titled(
        "AgileFFP - YAML Editor",
        Container(
            DivHStacked(
                # Left content (spans 2/3 width)
                Div(
                    id=charts_id,
                )(
                    H2("Main Content"),
                    P("This content spans the first two columns"),
                    cls="w-2/3",
                ),
                # Right content (spans 1/3 width)
                yaml_editor.initialize(session, charts_id),
                cls="gap-4",
            ),
        ),
    )


if __name__ == "__main__":
    print("----Development environment----")

    serve(appname="agileffp.app", app="app", reload=True)
