import json
from agileffp.devops.api import AzureDevOpsApi


class AzureDevOpsApiMock(AzureDevOpsApi):
    def __init__(self):
        AzureDevOpsApi.__init__(self, "none", "dev.azure.com", "acme", "gines")

    def _get_mock_data(json_file: str) -> dict:
        with open(f"tests/devops/mock_data/{json_file}", "r") as f:
            return json.loads(f.read())

    def get_work_items_from_query(self, query_id: str) -> dict:
        data = AzureDevOpsApiMock._get_mock_data("query_result.json")
        return data

    def get_work_item_fields(self, wit_id: str) -> dict:
        raise NotImplementedError()

    def get_work_item_updates(self, wit_id: str) -> dict:
        data = AzureDevOpsApiMock._get_mock_data("item_updates.json")
        for update in data["value"]:
            update["workItemId"] = wit_id
        return data
