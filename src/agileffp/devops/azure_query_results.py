import json
import base64
import http.client


def _get_from_azure(pat: str, server: str, org: str, project: str, uri: str) -> dict:
    conn = http.client.HTTPSConnection(server)
    payload = ""
    headers = {
        "Authorization": f"Basic {_toBase64(f':{pat}')}",
    }
    conn.request(
        "GET",
        f"/{org}/{project}{uri}",
        payload,
        headers,
    )
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))


def get_work_items_from_query(
    pat: str, server: str, org: str, project: str, query_id: str
) -> dict:
    return _get_from_azure(
        pat,
        server,
        org,
        project,
        f"/_apis/wit/wiql/{query_id}?api-version=7.1-preview.2",
    )


def get_work_item_fields(
    pat: str, server: str, org: str, project: str, wit_id: str
) -> dict:
    return _get_from_azure(
        pat,
        server,
        org,
        project,
        f"/_apis/wit/workitems/{wit_id}?api-version=7.1-preview.3",
    )


def get_work_item_updates(
    pat: str, server: str, org: str, project: str, wit_id: str
) -> dict:
    return _get_from_azure(
        pat,
        server,
        org,
        project,
        f"/_apis/wit/workItems/{wit_id}/updates?api-version=7.1-preview.3",
    )


def _toBase64(s: str) -> str:
    bytes = s.encode("utf-8")
    b64bytes = base64.b64encode(bytes)
    b64str = b64bytes.decode("utf-8")
    return b64str
