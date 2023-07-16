import pytest
from dateutil import parser

from agileffp.devops.azure_wit_states import AzureWitStates
from devops.api_mock import AzureDevOpsApiMock


@pytest.fixture
def api_mock():
    return AzureDevOpsApiMock()


@pytest.fixture
def wit_states(api_mock):
    return AzureWitStates(api_mock)


def assert_parse_state_update(api_mock):
    update = api_mock.get_work_item_updates("123")["value"][0]
    log = AzureWitStates._parse_state_update(update)
    assert len(log) == 3
    assert log == ["123", parser.parse("2023-06-13T11:54:07.583Z"), "New"]


def assert_states_table_colums(api_mock, wit_states):
    wit_list = api_mock.get_work_items_from_query("123")
    df = wit_states._get_wit_state_updates(wit_list)
    columns = df.columns.tolist()
    assert len(columns) == 3
    assert columns == ["id", "date", "state"]


def assert_states_are_parsed(api_mock, wit_states):
    wit_list = api_mock.get_work_items_from_query("123")
    wit_list["workItems"] = [wit_list["workItems"][0]]
    df = wit_states._get_wit_state_updates(wit_list)
    assert len(df) == 2


def assert_states_are_sorted(wit_states):
    wit_states._read_process_states()
    assert len(wit_states.states_list) == 5
    assert wit_states.states_list == ["New", "Approved", "Committed", "Done", "Removed"]


def assert_states_are_categorized(wit_states):
    wit_states._read_process_states()
    assert wit_states.proposed_states == ["New", "Approved"]
    assert wit_states.in_progress_states == ["Committed"]
    assert wit_states.done_states == ["Done"]
    assert wit_states.removed_states == ["Removed"]


def assert_states_are_registered(wit_states):
    df = wit_states.compute_states_from_query("123")
    assert len(df.columns) == 6
    assert len(df) == 74


def assert_states_dates_are_always_forward(wit_states):
    df = wit_states.compute_states_from_query("123")
    for _, row in df.iterrows():
        latest = None
        for col in df.columns:
            if col != "ids":
                if latest is not None and row[col] is not None:
                    assert latest <= row[col]
                    latest = row[col]


# TODO: Test to check states date when a work item has gone backwards in the process flow
# For this test, create mock data from item 165571
