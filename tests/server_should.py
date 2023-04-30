from agileffp import create_app


def assert_config():
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def assert_gantt_landing(client):
    response = client.get("/gantt", follow_redirects=True)
    assert response.status_code == 200
    assert b"Upload" in response.data
