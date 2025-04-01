
import pandas as pd
import plotly.express as px
from fasthtml.common import FT, NotStr, Table, Tbody, Td, Th, Thead, Tr
from monsterui.all import Card, DivVStacked

from agileffp.roadmap.models.epic import Epic
from agileffp.roadmap.models.planning import Planning


def render_charts(data: dict, target: str):
    planning = Planning(**data)

    # # timeline_tasks = (
    # #     [tl for c in capacity.values()
    # #      for tl in c.to_timeline()] if capacity else []
    # # )

    epics = [epic.to_dict(planning.teams) for epic in planning.sorted_epics]
    iterations = [it.to_dict(planning.teams) for it in planning.iterations]

    return DivVStacked(
        Card(render_planning_chart(planning.sorted_epics)),
        # Card(render_capacity_chart(timeline_tasks)) if capacity else None,
        Card(render_table(epics)),
        Card(render_table(iterations)),
        cls="container mt-8 mx-auto",
        id=target,
        hx_swap_oob="true",
    )


def render_planning_chart(epics: list[Epic]) -> FT:
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
