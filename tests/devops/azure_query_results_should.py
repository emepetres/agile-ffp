from agileffp.devops.azure_query_results import _toBase64


def assert_string_to_base64():
    assert _toBase64("hola caracola") == "aG9sYSBjYXJhY29sYQ=="
