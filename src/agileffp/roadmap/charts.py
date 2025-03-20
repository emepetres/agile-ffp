
import pandas as pd
import plotly.express as px
from fasthtml.common import FT, H2, NotStr, P, Table, Tbody, Td, Th, Thead, Tr
from monsterui.all import Card, DivVStacked

from agileffp.roadmap.gantt import Gantt
from agileffp.roadmap.models.epic import Epic


def initialize(target: str):
    return DivVStacked(
        Card(
            H2("Welcome to AgileFFP"),
            P("This is the main content area. Use the sidebar to load project information and generate charts."),
        ),
        id=target,
        hx_swap_oob="true",
        cls="container mt-8 mx-auto",
    )


def render_charts(data: dict, target: str):
    gantt = Gantt(**data)

    # # timeline_tasks = (
    # #     [tl for c in capacity.values()
    # #      for tl in c.to_timeline()] if capacity else []
    # # )

    epics = [epic.to_dict(gantt.teams) for epic in gantt.sorted_epics]
    iterations = [it.to_dict(gantt.teams) for it in gantt.iterations]

    return DivVStacked(
        Card(render_gantt_chart(gantt.sorted_epics)),
        # Card(render_capacity_chart(timeline_tasks)) if capacity else None,
        Card(render_table(epics)),
        Card(render_table(iterations)),
        cls="container mt-8 mx-auto",
        id=target,
        hx_swap_oob="true",
    )


def render_gantt_chart(epics: list[Epic]) -> FT:
    df = pd.DataFrame(
        [
            {
                "Epic": epic.name,
                "Start": epic.start,
                "Finish": epic.end,
                "Color": int((float(i)/len(epics))*100),
            }
            for i, epic in enumerate(epics)
        ]
    )

    fig1 = px.timeline(df, x_start="Start", x_end="Finish",
                       y="Epic", title="Project Timeline", template="plotly_dark", color="Color")
    fig1.update_yaxes(autorange="reversed")
    fig1.update_layout(
        showlegend=False,
        xaxis_title="Date",
        yaxis_title="Epics",
    )

    return NotStr(
        fig1.to_html(
            include_plotlyjs=False,
            full_html=False,
            config={"displayModeBar": False},
        )
    )


def render_table(items: list[dict]) -> FT:
    headers = items[0].keys()

    table = Table(
        Thead(Tr(*[Th(header.title()) for header in headers])),
        Tbody(*[Tr(*[Td(str(task[col])) for col in headers])
              for task in items]),
        cls="table",
    )

    return table


def render_capacity_chart(timeline_tasks: list) -> FT:
    df_capacity = pd.DataFrame(
        [
            {
                "Team": task["team"],
                "Start": task["start"],
                "Finish": task["end"],
                "Task": task["task"],
            }
            for task in timeline_tasks
        ]
    )

    fig2 = px.timeline(
        df_capacity,
        x_start="Start",
        x_end="Finish",
        y="Team",
        color="Task",
        title="Team Capacity Timeline",
        height=400,
        color_discrete_sequence=px.colors.qualitative.Set3,
        template="plotly_dark",
    )

    fig2.update_layout(
        showlegend=True,
        xaxis_title="Date",
        yaxis_title="Teams",
    )

    fig2.update_traces(marker_line_color="rgb(8,48,107)",
                       marker_line_width=1.5)

    return NotStr(
        fig2.to_html(
            include_plotlyjs=False, full_html=False, config={"displayModeBar": False}
        )
    )
