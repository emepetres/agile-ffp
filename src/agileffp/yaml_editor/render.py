from textwrap import dedent

import yaml
from fasthtml.common import (
    A,
    Code,
    Div,
    Img,
    Input,
    P,
    Pre,
)
from monsterui.all import (
    Button,
    ButtonT,
    DivHStacked,
    DivVStacked,
    TextT,
    UkIcon,
)

from agileffp.roadmap.charts import render_charts
from agileffp.yaml_editor import config


def initialize(session, name: str, yaml_content: str):
    session["yaml_filename"] = "No file loaded"
    session["yaml_content"] = yaml_content
    session["editor_hidden"] = False

    return (
        DivVStacked(
            P(name),
            id=config.CHARTS_TARGET,
            cls="container mt-8 mx-auto",
        ),
        render(session),
    )


def render(session, update_editor: bool = True, update_charts: bool = True):
    editor, charts = None, None
    if update_editor:
        editor = _render_editor_hidden() if session["editor_hidden"] else _render_editor_visible(
            session["yaml_filename"], session["yaml_content"])

    if update_charts:
        try:
            yaml_data = yaml.safe_load(
                session["yaml_content"]) if session["yaml_content"] else None
            charts = render_charts(
                yaml_data, config.CHARTS_TARGET) if yaml_data else None
        except yaml.YAMLError as e:
            charts = Div(
                f"Invalid YAML format: {str(e)}", cls=TextT.error, hx_swap_oob=True, id=config.CHARTS_TARGET)
        except Exception as e:
            charts = Div(
                f"Error processing YAML: {str(e)}", cls=TextT.error, hx_swap_oob=True, id=config.CHARTS_TARGET)

    return editor, charts


def _render_editor_visible(filename: str, yaml_content: str):
    return (
        Div(
            id="yaml-editor-container",
            cls="w-[400px] border-l border-border uk-animation-slide-right-medium fixed top-0 right-0 h-screen",
        )(
            DivHStacked(
                # Sidebar toggle button
                Div(
                    Button(UkIcon("chevron-right"), cls=ButtonT.ghost),
                    hx_get=config.Endpoints.TOGGLE_EDITOR.with_prefix(),
                    hx_target="#yaml-editor-container",
                    hx_swap="outerHTML",
                    style="position: fixed; top: 0;"
                ),
                # Template button
                Button(
                    Img(src="images/template_icon.svg",
                        cls="w-6 h-6 inline-block"),
                    alt="Load template",
                    cls=(ButtonT.primary, "mt-14"),
                    hx_put=config.Endpoints.UPLOAD_TEMPLATE.with_prefix(),
                    hx_target="#editor-container",
                    hx_indicator="#spinner",
                    style="width: auto !important"
                ),
                # File input with drag & drop zone
                Div(
                    Input(
                        type="file",
                        id="file",
                        name="file",
                        hx_encoding="multipart/form-data",
                        hx_put=config.Endpoints.UPLOAD.with_prefix(),
                        hx_trigger="change",
                        hx_target="#editor-container",
                        hx_indicator="#spinner",
                        style="",
                    ),
                    P("or drag files here", cls=(TextT.muted, "text-center")),
                    cls="mb-4 border border-blue-500 rounded mt-2 mr-2",
                ),
            ),
            # Editor container
            _render_yaml_content(filename, yaml_content),
        ),
    )


def _render_editor_hidden():
    return Div(
        id="yaml-editor-container",
        cls="w-[50px] border-l border-border uk-animation-slide-left-medium fixed top-0 right-0 h-screen",
    )(
        # Sidebar toggle button
        Div(
            Button(UkIcon("chevron-left"), cls=ButtonT.ghost),
            hx_get=config.Endpoints.TOGGLE_EDITOR.with_prefix(),
            hx_target="#yaml-editor-container",
            hx_swap="outerHTML",
        ),
    )


def _render_yaml_content(filename: str, yaml_content: str | None):
    if not yaml_content:
        yaml_content = "No content loaded"
    return Div(
        Div(
            P(f"File: {filename}", cls=[
                TextT.success, "font-mono px-4 w-[400px]"]),
            Div(
                Button(UkIcon("save"),
                       cls=[ButtonT.ghost, "h-6 w-6 p-0"],
                       hx_put=config.Endpoints.SAVE_YAML.with_prefix(),
                       hx_target="this",
                       hx_swap="none",
                       hx_indicator="#spinner",
                       aria_label="Save YAML"),
                Button(UkIcon("trash"),
                       cls=[ButtonT.ghost, "h-6 w-6 p-0"],
                       aria_label="Delete YAML"),
                A("Help?", cls=[TextT.info, "font-mono"],
                  hx_get=config.Endpoints.HELP.with_prefix(),
                  hx_target="#help-container",
                  ),
                cls="flex items-center gap-2 px-4"
            ),
            cls="flex justify-between",
        ),
        Pre(
            Code(yaml_content,
                 contenteditable=True,
                 id="yaml-editor",
                 hx_post=config.Endpoints.UPDATE_YAML.with_prefix(),
                 hx_target=f"#{config.CHARTS_TARGET}",
                 hx_trigger="change, keyup delay:0.5s",
                 hx_vals='js:{yaml_content: document.getElementById("yaml-editor").innerText}',
                 name="yaml_content",
                 spellcheck="false",
                 wrap="soft",
                 cls="uk-codeblock"
                 ),
            cls=(
                f'bg-gray-100 dark:bg-gray-800 {TextT.gray} p-0.4 rounded text-sm font-mono language-yaml'),
            style="resize: none; font-size: 14px; height: calc(100vh - 150px);",
        ),
        Div(
            id="help-container",
        ),
        id="editor-container",
        cls="uk-codeblock space-y-4",
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
