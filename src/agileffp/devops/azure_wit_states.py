import pandas as pd
from dateutil import parser
from agileffp.devops.api import AzureDevOpsApi


class AzureWitStates:
    def __init__(self, api: AzureDevOpsApi):
        self.api = api
        self.initialized = False

    def initialize(self):
        if not self.initialized:
            self._read_process_states()
            self.initialized = True

    def compute_states_from_query(self, query_id: str) -> pd.DataFrame:
        self.initialize()
        wit_list = self.api.get_work_items_from_query(query_id)
        df = self._get_wit_state_updates(wit_list)
        states = self._compute_work_items_states(df)
        return states

    def _compute_work_items_states(self, df: pd.DataFrame) -> pd.DataFrame:
        """Computes work items states from a time-series format table."""
        # first flat the ts table creating a column per state
        flat_states = {}
        for _, row in df.iterrows():
            wid = row["id"]
            if wid not in flat_states:
                flat_states[wid] = {}
            state = row["state"]
            if state not in flat_states[wid]:
                flat_states[wid][state] = row["date"]
            else:
                current_date = flat_states[wid][state]
                new_date = row["date"]
                if (self._is_ending_state(state) and new_date > current_date) or (
                    not self._is_ending_state(state) and new_date < current_date
                ):
                    flat_states[wid][state] = row["date"]
        data = {"id": []}

        # then define the columns and rows of the new table
        for state in self.states_list:
            data[state] = []
        for wit_id, state_changes in flat_states.items():
            data["id"].append(wit_id)
            for state in self.states_list:
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
                parser.parse(update["fields"]["System.ChangedDate"]["newValue"]),
                update["fields"]["System.State"]["newValue"],
            ]
        else:
            return []

    def _get_wit_metadata(data: dict) -> pd.DataFrame:
        """Transforms work items metadata into a pandas DataFrame."""
        raise NotImplementedError()

    def _read_process_states(self):
        """Creates a list of work items states sorted by devops process.

        Also separate these process states into categories."""
        data = self.api.get_wit_states()
        sorted_data = sorted(data["value"], key=lambda x: x["order"])
        self.states_list = [state["name"] for state in sorted_data]
        self.proposed_states = [
            state["name"]
            for state in sorted_data
            if state["stateCategory"] == "Proposed"
        ]
        self.in_progress_states = [
            state["name"]
            for state in sorted_data
            if state["stateCategory"] == "InProgress"
        ]
        self.done_states = [
            state["name"]
            for state in sorted_data
            if state["stateCategory"] == "Completed"
        ]
        self.removed_states = [
            state["name"]
            for state in sorted_data
            if state["stateCategory"] == "Removed"
        ]

    def _is_ending_state(self, state: str) -> bool:
        """Checks if a state is an ending state."""
        return state in self.done_states or state in self.removed_states
