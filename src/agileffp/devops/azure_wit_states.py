from typing import Callable
import pandas as pd
from dateutil import parser
from agileffp.devops import config
from agileffp.devops.azure_query_results import (
    get_work_items_from_query,
)


def compute_states_from_query() -> pd.DataFrame:
    data = get_work_items_from_query(
        config.PAT, config.SERVER, config.ORGANIZATION, config.PROJECT, config.QUERY_ID
    )
    states = compute_work_items_states(data)
    return states


def compute_work_items_states(data: dict) -> pd.DataFrame:
    raise NotImplementedError()


def _get_wit_ids_list(data: dict) -> list:
    """Returns a list of work items ids from a query result."""
    return [wit["id"] for wit in data["workItems"]]


def get_wit_state_updates(
    data: dict, wit_getter: Callable[[str, str, str, str, str], dict]
) -> pd.DataFrame:
    """Writes work items state updates in a time-series format table."""
    parsed_updates = []
    wit_list = _get_wit_ids_list(data)
    for wit_id in wit_list:
        wit_updates = wit_getter(
            config.PAT, config.SERVER, config.ORGANIZATION, config.PROJECT, wit_id
        )
        for update in wit_updates["value"]:
            update_data = parse_state_update(update)
            if update_data:
                parsed_updates.append(update_data)
    df = pd.DataFrame(parsed_updates, columns=["id", "date", "state"])
    return df


def parse_state_update(update: dict) -> list:
    """Parses a work item state update."""
    if "fields" in update and "System.State" in update["fields"]:
        return [
            update["workItemId"],
            parser.parse(update["revisedDate"]),
            update["fields"]["System.State"]["newValue"],
        ]
    else:
        return []


def get_wit_metadata(data: dict) -> pd.DataFrame:
    """Transforms work items metadata into a pandas DataFrame."""
    raise NotImplementedError()
