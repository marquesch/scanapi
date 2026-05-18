from pytest import fixture

from scanapi.tree.endpoint_node import EndpointNode


@fixture
def endpoint_node():
    return EndpointNode(
        {
            "endpoints": [
                {
                    "name": "foo",
                    "requests": [
                        {
                            "name": "First",
                            "path": "http://foo.com/first",
                        },
                        {
                            "name": "Second",
                            "path": "http://foo.com/second",
                        },
                    ],
                }
            ],
            "name": "node",
            "requests": [],
        }
    )


@fixture
def flat_endpoint_node():
    return EndpointNode(
        {
            "endpoints": [
                {
                    "name": "foo",
                    "requests": [],
                }
            ],
            "name": "node",
            "requests": [
                {
                    "name": "First",
                    "path": "http://foo.com/first",
                },
                {
                    "name": "Second",
                    "path": "http://foo.com/second",
                },
            ],
        }
    )
