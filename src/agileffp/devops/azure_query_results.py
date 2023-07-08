import json
import base64
import http.client


def get_work_items_from_query(
    pat: str, server: str, org: str, project: str, query_id: str
) -> dict:
    conn = http.client.HTTPSConnection(server)
    payload = ""
    headers = {
        "Authorization": f"Basic {_toBase64(f':{pat}')}",
    }
    conn.request(
        "GET",
        f"/{org}/{project}/_apis/wit/wiql/{query_id}?api-version=7.1-preview.2",
        payload,
        headers,
    )
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))


def _toBase64(s: str) -> str:
    bytes = s.encode("utf-8")
    b64bytes = base64.b64encode(bytes)
    b64str = b64bytes.decode("utf-8")
    return b64str
