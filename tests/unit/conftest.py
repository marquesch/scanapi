import requests
from pytest import fixture


@fixture
def fake_results():
    return {
        "name": "root",
        "path": "/root",
        "request_results": [
            {"response": "foo", "tests_results": [], "no_failure": True},
            {"response": "bar", "tests_results": [], "no_failure": False},
        ],
        "child_endpoints": [
            {
                "name": "root::user",
                "path": "/root/user",
                "request_results": [
                    {"response": "baz", "test_results": [], "no_failure": True},
                ],
                "child_endpoints": [],
            },
            {
                "name": "root::group",
                "path": "/root/group",
                "request_results": [
                    {
                        "response": "quux",
                        "test_results": [],
                        "no_failure": False,
                    }
                ],
                "child_endpoints": [],
            },
        ],
    }


@fixture
def response(requests_mock):
    requests_mock.get("http://test.com", text="data")
    return requests.get("http://test.com")


@fixture
def structured_result(response):
    return {
        "name": "root",
        "path": "/root",
        "request_results": [response],
        "child_endpoints": [],
    }
