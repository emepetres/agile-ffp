import json
import base64
import http.client


class AzureDevOpsApi:
    def __init__(
        self,
        pat: str,
        server: str,
        org: str,
        project: str,
        process_id: str,
        wit_type_ref: str,
    ):
        self.pat = pat
        self.server = server
        self.org = org
        self.project = project
        self.process_id = process_id
        self.wit_type_ref = wit_type_ref

    def _get_from_azure(self, uri: str) -> dict:
        conn = http.client.HTTPSConnection(self.server)
        payload = ""
        headers = {
            "Authorization": f"Basic {_toBase64(f':{self.pat}')}",
        }
        conn.request(
            "GET",
            f"/{self.org}{uri}",
            payload,
            headers,
        )
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))

    def get_work_items_from_query(self, query_id: str) -> dict:
        return self._get_from_azure(
            f"/{self.project}/_apis/wit/wiql/{query_id}?api-version=7.1-preview.2",
        )

    def get_work_item_fields(self, wit_id: str) -> dict:
        return self._get_from_azure(
            f"/{self.project}/_apis/wit/workitems/{wit_id}?api-version=7.1-preview.3",
        )

    def get_work_item_updates(self, wit_id: str) -> dict:
        return self._get_from_azure(
            f"/{self.project}/_apis/wit/workItems/{wit_id}/updates?api-version=7.1-preview.3",
        )

    def get_wit_states(self) -> dict:
        return self._get_from_azure(
            f"/_apis/work/processes/{self.process_id}/workItemTypes/{self.wit_type_ref}/states?api-version=7.1-preview.1",
        )


def _toBase64(s: str) -> str:
    bytes = s.encode("utf-8")
    b64bytes = base64.b64encode(bytes)
    b64str = b64bytes.decode("utf-8")
    return b64str
