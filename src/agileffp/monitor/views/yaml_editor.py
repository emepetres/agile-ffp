from datetime import datetime
from textwrap import dedent

from fasthtml.common import (
    A,
    Code,
    DialogX,
    Div,
    Form,
    Input,
    Label,
    P,
    Pre,
    Span,
)
from monsterui.all import (
    Button,
    ButtonT,
    DivHStacked,
    TextT,
    UkIcon,
)

from agileffp.monitor import routes


def render(editor_hidden: bool, version: str, yaml_content: str, prev_version: str, next_version: str, charts_target: str):
    editor = _render_editor_hidden(version) if editor_hidden else _render_editor_visible(
        version, yaml_content, prev_version, next_version, charts_target)

    return editor


def _render_editor_visible(version: str, yaml_content: str, prev_version: str, next_version: str, charts_target: str):
    if not yaml_content:
        yaml_content = "No content loaded"

    return (
        Div(
            id="yaml-editor-container",
            cls="w-[400px] border-l border-border uk-animation-slide-right-medium fixed top-0 right-0 h-screen",
        )(
            DivHStacked(
                # Sidebar toggle button
                Div(
                    Button(UkIcon("chevron-right"), cls=ButtonT.ghost),
                    hx_get=f"{routes.Endpoints.TOGGLE_EDITOR.with_prefix()}?hide=true&version={version}",
                    hx_target="#yaml-editor-container",
                    hx_swap="outerHTML",
                    style="position: fixed; top: 0;"
                ),
            ),
            Div(
                render_controls(version, prev_version,
                                next_version, swap=False),
                render_source_editor(yaml_content, charts_target, swap=False),
                Div(
                    id="dialog-container",
                ),
                id="editor-container",
                cls="uk-codeblock space-y-4",
            )
        )
    )


def render_controls(version: str, prev_version: str, next_version: str, swap: bool = True):
    controls = Div(
        Div(
            Div(
                Button(UkIcon("save"),
                       cls=[ButtonT.ghost, "h-6 w-6 p-0"],
                       hx_get=routes.Endpoints.SAVE_VERSION_DIALOG.with_prefix(),
                       hx_target="#dialog-container",
                       hx_indicator="#spinner",
                       aria_label="Save YAML"),
                Button(UkIcon("download"),  # FIXME: does nothing
                       cls=[ButtonT.ghost, "h-6 w-6 p-0"],
                       hx_put=routes.Endpoints.DOWNLOAD_YAML.with_prefix(),
                       hx_vals='js:{yaml_content: document.getElementById("yaml-editor").innerText}',
                       hx_swap="none",
                       hx_indicator="#spinner",
                       aria_label="Download YAML",
                       hx_ext="response-targets",
                       disabled=True),
                Button(UkIcon("upload"),
                       cls=[ButtonT.ghost, "h-6 w-6 p-0"],
                       hx_get=routes.Endpoints.UPLOAD_DIALOG.with_prefix(),
                       hx_target="#dialog-container",
                       aria_label="Upload YAML"),
                Button(UkIcon("file-text"),
                       cls=[ButtonT.ghost, "h-6 w-6 p-0"],
                       hx_put=routes.Endpoints.UPLOAD_TEMPLATE.with_prefix(),
                       hx_target="#editor-container",
                       hx_indicator="#spinner",
                       aria_label="Load template"),
                A("Help?", cls=[TextT.primary, "font-mono"],
                  hx_get=routes.Endpoints.HELP.with_prefix(),
                  hx_target="#dialog-container",
                  ),
                cls="flex items-center gap-2 px-4"
            ),
            cls="flex justify-end",
            style="margin: 1em;"
        ),
        # Version navigation
        Div(
            Div(
                Span(
                    version,
                    cls="font-mono text-sm max-w-[250px]",
                ),
                Button(UkIcon("chevron-left"),
                       cls=[ButtonT.ghost, "h-6 w-6 p-0"],
                       hx_get=routes.Endpoints.VERSION.with_prefix() +
                       f"?version={prev_version}",
                       hx_target="#yaml-editor-container",
                       hx_indicator="#spinner",
                       disabled=prev_version is None,
                       aria_label="Previous Version"),
                Button(UkIcon("chevron-right"),
                       cls=[ButtonT.ghost, "h-6 w-6 p-0"],
                       hx_get=routes.Endpoints.VERSION.with_prefix() +
                       f"?version={next_version}",
                       hx_target="#yaml-editor-container",
                       hx_indicator="#spinner",
                       disabled=next_version is None,
                       aria_label="Next Version"),
                cls="flex items-center gap-2",
            ),
            id="version-navigation",
            cls="flex gap-2 justify-end pr-4",
            style="margin-right: 1em;"
        ),
        id="editor-controls-container",
    )

    if swap:
        controls.hx_swap_oob = "true"

    return controls


def render_source_editor(yaml_content: str, charts_target: str, swap: bool = True):
    editor = Pre(
        Code(yaml_content,
             contenteditable=True,
             id="yaml-editor",
             hx_post=routes.Endpoints.UPDATE_YAML.with_prefix(),
             hx_target=f"#{charts_target}",
             hx_trigger="change, keyup delay:0.5s",
             hx_vals='js:{yaml_content: document.getElementById("yaml-editor").innerText}',
             name="yaml_content",
             spellcheck="false",
             wrap="soft",
             cls="uk-codeblock"
             ),
        cls=(
            f'bg-gray-100 dark:bg-gray-800 {TextT.gray} rounded text-sm font-mono language-yaml'),
        style="resize: none; font-size: 14px; height: calc(100vh - var(--editor-controls-height, 80px)); margin: 0;",
        id="editor-source-container",
    )

    if swap:
        editor.hx_swap_oob = "true"

    return editor


def _render_editor_hidden(version: str):
    return Div(
        id="yaml-editor-container",
        cls="w-[50px] border-l border-border uk-animation-slide-left-medium fixed top-0 right-0 h-screen",
    )(
        # Sidebar toggle button
        Div(
            Button(UkIcon("chevron-left"), cls=ButtonT.ghost),
            hx_get=f"{routes.Endpoints.TOGGLE_EDITOR.with_prefix()}?hide=false&version={version}",
            hx_target="#yaml-editor-container",
            hx_swap="outerHTML",
        ),
    )


def render_upload_dialog():
    hdr = Div(
        P("Upload a YAML file"),
        Button(UkIcon("x"),
               aria_label="Close",
               hx_get=routes.Endpoints.HELP.with_prefix(),
               hx_target="#upload-dialog",
               hx_swap="delete",
               cls=(ButtonT.ghost, "h-9 w-9 p-0"),
               style="width: 2.25rem;"
               ),
        cls="flex justify-between items-center px-4 py-1"
    )
    return DialogX(
        # File input with drag & drop zone
        Div(
            Input(
                type="file",
                id="file",
                name="file",
                hx_encoding="multipart/form-data",
                hx_put=routes.Endpoints.UPLOAD.with_prefix(),
                hx_trigger="change",
                hx_target="#editor-container",
                hx_indicator="#spinner",
                style="",
            ),
            P("or drag files here", cls=(TextT.muted, "text-center")),
            cls="mb-4 border border-blue-500 rounded mt-2 mr-2",
        ),
        header=hdr,
        open=True,
        id='upload-dialog'
    )


def render_save_version_dialog(yaml_content: str):
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    hdr = Div(
        P("Save Version"),
        Button(UkIcon("x"),
               aria_label="Close",
               hx_get=routes.Endpoints.SAVE_VERSION_DIALOG.with_prefix(),
               hx_target="#save-version-dialog",
               hx_swap="delete",
               cls=(ButtonT.ghost, "h-9 w-9 p-0"),
               style="width: 2.25rem;"
               ),
        cls="flex justify-between items-center px-4 py-1"
    )

    return DialogX(
        Form(
            Div(
                Label("Version Name", for_="version_name"),
                Input(
                    type="text",
                    id="version_name",
                    name="version_name",
                    value=f"Version-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    placeholder="Enter version name",
                    cls="w-full px-2 py-1 rounded border mb-4",
                    required=True
                ),
                cls="mb-4"
            ),
            Div(
                Label("Date", for_="version_date"),
                Input(
                    type="text",
                    id="version_date",
                    name="version_date",
                    value=current_date,
                    placeholder="YYYY-MM-DD HH:MM:SS",
                    cls="w-full px-2 py-1 rounded border mb-4",
                    required=True
                ),
                cls="mb-4"
            ),
            Div(
                Button("Save",
                       type="submit",
                       cls=ButtonT.primary,
                       hx_post=routes.Endpoints.SAVE_YAML.with_prefix(),
                       hx_vals='js:{yaml_content: document.getElementById("yaml-editor").innerText}',
                       hx_target="#save-version-dialog",
                       hx_swap="delete"),
                cls="flex justify-between"
            ),
            hx_encoding="multipart/form-data",
        ),
        header=hdr,
        open=True,
        id='save-version-dialog'
    )


def render_help_dialog():
    hdr = Div(
        P("Help Information"),
        Button(UkIcon("x"),
               aria_label="Close",
               hx_get=routes.Endpoints.HELP.with_prefix(),
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


def get_default_template() -> str:
    return dedent(
        """
            teams:
                - name: AI
                  days: 247
                  members:
                    - Gabriel
                    - Iker
                - name: 3D
                  days: 500
                  members:
                    - Marcos

            iterations:
                - name: Sprint 1
                  start: 2025-01-05
                  end: 2025-01-18
                  capacity:
                    Gabriel: 9
                    Iker: 8
                    Marcos: 7
                  closed:
                    Gabriel:
                        epic_one: 2
                        epic_two: 2
                    Iker:
                        epic_one: 4
                    Marcos:
                        epic_one: 3
                - name: Sprint 2
                  start: 2025-01-19
                  end: 2025-02-01
                  capacity:
                    Gabriel: 8
                    Iker: 7
                    Marcos: 6
                  closed:
                    Gabriel:
                        epic_two: 3
                    Iker:
                        epic_two: 3
                    Marcos:
                        epic_two: 2

            default_iteration:
                index: 3
                prefix: "Sprint "
                days_interval: 15
                capacity:
                    Gabriel: 8
                    Iker: 8
                    Marcos: 6

            epics:
                - name: epic_one
                  items:
                    AI: 6
                    3D: 3
                - name: epic_two
                  items:
                    AI: 10
                    3D: 5
                  depends_on:
                    - epic_one
                - name: epic_three
                  items:
                    AI: 8
                    3D: 4
                  planned:
                    Gabriel: 2
                    Iker: -1
                    Marcos: 2
                  priority: 60
                  depends_on:
                    - epic_one
        """
    ).strip()
