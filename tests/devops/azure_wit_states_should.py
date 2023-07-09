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
    log = AzureWitStates.parse_state_update(update)
    assert len(log) == 3
    assert log == [168975, parser.parse("2023-06-13T11:57:06.947Z"), "New"]


def assert_states_table_colums(api_mock, wit_states):
    wit_list = api_mock.get_work_items_from_query("123")
    df = wit_states.get_wit_state_updates(wit_list)
    columns = df.columns.tolist()
    assert len(columns) == 3
    assert columns == ["id", "date", "state"]


def assert_states_are_parsed(api_mock, wit_states):
    wit_list = api_mock.get_work_items_from_query("123")
    df = wit_states.get_wit_state_updates(wit_list)
    assert len(df) == 6
