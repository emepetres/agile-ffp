import pandas as pd
from agileffp.devops import config
from agileffp.devops.azure_query_results import get_work_items_from_query


def compute_states_from_query() -> pd.DataFrame:
    data = get_work_items_from_query(
        config.PAT, config.SERVER, config.ORGANIZATION, config.PROJECT, config.QUERY_ID
    )
    states = compute_work_items_states(data)
    return states


def compute_work_items_states(data: dict) -> pd.DataFrame:
    df = pd.DataFrame(columns=[wit["name"] for wit in data["columns"]])
    return df
