from pytest import mark, raises

from scanapi.errors import InvalidKeyError, MissingMandatoryKeyError
from scanapi.utils import (
    flatten_endpoint_results,
    join_urls,
    session_with_retry,
    validate_keys,
)


@mark.describe("utils")
@mark.describe("join_urls")
class TestJoinUrls:
    test_data = [
        (
            "http://demo.scanapi.dev/api/",
            "health",
            "http://demo.scanapi.dev/api/health",
        ),
        (
            "http://demo.scanapi.dev/api/",
            "/health",
            "http://demo.scanapi.dev/api/health",
        ),
        (
            "http://demo.scanapi.dev/api/",
            "/health/",
            "http://demo.scanapi.dev/api/health/",
        ),
        (
            "http://demo.scanapi.dev/api",
            "health",
            "http://demo.scanapi.dev/api/health",
        ),
        (
            "http://demo.scanapi.dev/api",
            "/health",
            "http://demo.scanapi.dev/api/health",
        ),
        (
            "http://demo.scanapi.dev/api",
            "/health/",
            "http://demo.scanapi.dev/api/health/",
        ),
        (
            "",
            "http://demo.scanapi.dev/api/health/",
            "http://demo.scanapi.dev/api/health/",
        ),
        (
            "http://demo.scanapi.dev/api/health/",
            "",
            "http://demo.scanapi.dev/api/health/",
        ),
        ("", "", ""),
    ]

    @mark.it("should build url properly")
    @mark.parametrize("url_1, url_2, expected", test_data)
    def test_build_url_properly(self, url_1, url_2, expected):
        assert join_urls(url_1, url_2) == expected


@mark.describe("utils")
@mark.describe("validate_keys")
class TestValidateKeys:
    @mark.context("there is an invalid key")
    @mark.it("should raise an exception")
    def test_should_raise_an_exception(self):
        keys = ["key1", "key2"]
        available_keys = ("key1", "key3")
        mandatory_keys = ("key1", "key2")
        scope = "endpoint"

        with raises(InvalidKeyError) as excinfo:
            validate_keys(keys, available_keys, mandatory_keys, scope)

        assert (
            str(excinfo.value)
            == "Invalid key 'key2' at 'endpoint' scope. Available keys are: ('key1', 'key3')"
        )

    @mark.context("there is a mandatory key missing")
    @mark.it("should raise an exception")
    def test_should_raise_an_exception_2(self):
        keys = ["key1"]
        available_keys = ("key1", "key3")
        mandatory_keys = ("key1", "key2")
        scope = "endpoint"

        with raises(MissingMandatoryKeyError) as excinfo:
            validate_keys(keys, available_keys, mandatory_keys, scope)

        assert str(excinfo.value) == "Missing 'key2' key(s) at 'endpoint' scope"

    @mark.context("there is not an invalid key or a mandatory key missing")
    @mark.it("should not raise an exception")
    def test_should_not_raise_an_exception(self):
        keys = ["key1"]
        available_keys = ("key1", "key3")
        mandatory_keys = ("key1",)
        scope = "endpoint"

        validate_keys(keys, available_keys, mandatory_keys, scope)


@mark.describe("utils")
@mark.describe("session_with_retry")
class TestSessionWithRetry:
    @mark.context("there is no retry configuration")
    @mark.it("should not mount custom adapters")
    def test_should_not_mount_custom_adapters(self):
        session = session_with_retry({})

        assert session._transport._pool._retries == 0

    @mark.context("there is a retry configuration")
    @mark.it("should mount custom adapters")
    def test_should_mount_custom_adapters(self):
        session = session_with_retry({"max_retries": 7})

        assert session._transport._pool._retries == 7


@mark.describe("utils")
@mark.describe("flatten_results")
class TestFlattenResults:
    test_data = [
        (
            # endpoint_result
            {
                "name": "root",
                "path": "/root",
                "request_results": [],
                "endpoint_results": [
                    {
                        "name": "root::user",
                        "path": "/root/user",
                        "request_results": [
                            {
                                "response": "baz",
                                "test_results": [],
                                "no_failure": True,
                            },
                        ],
                        "endpoint_results": [],
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
                        "endpoint_results": [],
                    },
                ],
            },
            # flat_result
            [
                {"response": "baz", "test_results": [], "no_failure": True},
                {"response": "quux", "test_results": [], "no_failure": False},
            ],
        ),
        (
            # endpoint_result
            {
                "name": "root",
                "path": "/root",
                "request_results": [
                    {
                        "response": "foo",
                        "tests_results": [],
                        "no_failure": True,
                    },
                    {
                        "response": "bar",
                        "tests_results": [],
                        "no_failure": False,
                    },
                ],
                "endpoint_results": [],
            },
            # flat_result
            [
                {"response": "foo", "tests_results": [], "no_failure": True},
                {"response": "bar", "tests_results": [], "no_failure": False},
            ],
        ),
    ]

    @mark.context("results are structured")
    @mark.it("should flatten all results into one single iterator")
    @mark.parametrize("endpoint_result, flat_result", test_data)
    def test_flatten_results(self, endpoint_result, flat_result):
        flattened_endpoint_results = [
            o for o in flatten_endpoint_results(endpoint_result)
        ]
        assert list(flattened_endpoint_results) == flat_result
