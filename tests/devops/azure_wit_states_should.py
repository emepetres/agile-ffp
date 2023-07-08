import pytest
from agileffp.devops.azure_wit_states import compute_work_items_states

@pytest.fixture
def data():
    return {
        "queryType": "flat",
        "queryResultType": "workItem",
        "asOf": "2021-03-01T09:00:00Z",
        "columns": [
            {"name": "Id", "referenceName": "System.Id", "url": "https://dev.azure.com/organization/project/_apis/wit/fields/System.Id"},
            {"name": "Title", "referenceName": "System.Title", "url": "https://dev.azure.com/organization/project/_apis/wit/fields/System.Title"},
            {"name": "State", "referenceName": "System.State", "url": "https://dev.azure.com/organization/project/_apis/wit/fields/System.State"},
            {"name": "Work Item Type", "referenceName": "System.WorkItemType", "url": "https://dev.azure.com/organization/project/_apis/wit/fields/System.WorkItemType"},
        ],
        "workItems": [
            {"id": "123456", "url": "https://dev.azure.com/organization/project/_apis/wit/workItems/123456"},
            {"id": "123457", "url": "https://dev.azure.com/organization/project/_apis/wit/workItems/123457"},
            {"id": "123458", "url": "https://dev.azure.com/organization/project/_apis/wit/workItems/123458"},
            {"id": "123459", "url": "https://dev.azure.com/organization/project/_apis/wit/workItems/123459"},
            {"id": "123460", "url": "https://dev.azure.com/organization/project/_apis/wit/workItems/123460"},
            {"id": "123461", "url": "https://dev.azure.com/organization/project/_apis/wit/workItems/123461"},
        ]
    }

def assert_columns_are_parsed(data):
    df = compute_work_items_states(data)
    columns = df.columns.tolist()
    assert len(columns) == 4
    assert columns == ["Id", "Title", "State", "Work Item Type"]
