import json
from enum import Enum
from agileffp.devops.api import AzureDevOpsApi


class AzureDevOpsApiMock(AzureDevOpsApi):
    class MockBehaviour(Enum):
        EMPTY = 1
        SIMPLE = 2
        COMPLEX = 3

    def __init__(self, bhv: MockBehaviour):
        AzureDevOpsApi.__init__(self, "none", "dev.azure.com", "acme", "gines")
        self.bhv = bhv

    def _get_mock_data(json_file: str) -> dict:
        with open(f"tests/devops/mock_data/{json_file}", "r") as f:
            return json.loads(f.read())

    def get_work_items_from_query(self, query_id: str) -> dict:
        data = AzureDevOpsApiMock._get_mock_data("query_result.json")
        if self.bhv == AzureDevOpsApiMock.MockBehaviour.EMPTY:
            data["workItems"] = []

        return data

    def get_work_item_fields(self, wit_id: str) -> dict:
        raise NotImplementedError()

    def get_work_item_updates(self, wit_id: str) -> dict:
        data = AzureDevOpsApiMock._get_mock_data("item_updates.json")
        if self.bhv == AzureDevOpsApiMock.MockBehaviour.EMPTY:
            data["value"] = []
        elif self.bhv == AzureDevOpsApiMock.MockBehaviour.SIMPLE:
            data["value"] = [data["value"][0]]

        return data
