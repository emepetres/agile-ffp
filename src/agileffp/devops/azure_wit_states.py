from typing import List
import pandas as pd
from dateutil import parser
from agileffp.devops.api import AzureDevOpsApi


class AzureWitStates:
    def __init__(self, api: AzureDevOpsApi):
        self.api = api

    def compute_states_from_query(self, query_id: str) -> pd.DataFrame:
        wit_list = self.api.get_work_items_from_query(query_id)
        df = self._get_wit_state_updates(wit_list)
        states = self._compute_work_items_states(df)
        return states

    def _compute_work_items_states(self, df: pd.DataFrame) -> pd.DataFrame:
        """Computes work items states from a time-series format table."""
        # first flat the ts table creating a column per state
        flat_states = {}
        for _, row in df.iterrows():
            if row["id"] not in flat_states:
                flat_states[row["id"]] = {}
            flat_states[row["id"]][row["state"]] = row["date"]
        data = {"ids": []}
        # then define the columns and rows of the new table
        process_states = self._get_wit_states_sorted()
        for state in process_states:
            data[state] = []
        for wit_id, state_changes in flat_states.items():
            data["ids"].append(wit_id)
            for state in process_states:
                if state in state_changes:
                    data[state].append(state_changes[state])
                else:
                    data[state].append(None)
        return pd.DataFrame(data)

    def _get_wit_state_updates(self, data: dict) -> pd.DataFrame:
        """Writes work items state updates in a time-series format table."""
        parsed_updates = []
        wit_list = AzureWitStates._get_wit_ids_list(data)
        for wit_id in wit_list:
            wit_updates = self.api.get_work_item_updates(wit_id)
            for update in wit_updates["value"]:
                update_data = AzureWitStates._parse_state_update(update)
                if update_data:
                    parsed_updates.append(update_data)
        df = pd.DataFrame(parsed_updates, columns=["id", "date", "state"])
        return df

    def _get_wit_ids_list(data: dict) -> list:
        """Returns a list of work items ids from a query result."""
        return [wit["id"] for wit in data["workItems"]]

    def _parse_state_update(update: dict) -> list:
        """Parses a work item state update."""
        if "fields" in update and "System.State" in update["fields"]:
            return [
                update["workItemId"],
                parser.parse(update["revisedDate"]),
                update["fields"]["System.State"]["newValue"],
            ]
        else:
            return []

    def _get_wit_metadata(data: dict) -> pd.DataFrame:
        """Transforms work items metadata into a pandas DataFrame."""
        raise NotImplementedError()

    def _get_wit_states_sorted(self) -> List:
        """Returns a list of work items states sorted by devops process."""
        data = self.api.get_wit_states()
        sorted_data = sorted(data["value"], key=lambda x: x["order"])
        return [state["name"] for state in sorted_data]
