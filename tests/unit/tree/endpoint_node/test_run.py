import logging

from httpx import HTTPError
from pytest import fixture, mark

from scanapi.exit_code import ExitCode

log = logging.getLogger(__name__)


@mark.describe("endpoint node")
@mark.describe("run")
class TestRun:
    @fixture
    def mock_run_request(self, mocker):
        return mocker.patch("scanapi.tree.request_node.RequestNode.run")

    @fixture
    def mock_session(self, mocker):
        return mocker.patch("scanapi.tree.endpoint_node.session")

    @mark.context("when there are nested endpoint nodes")
    @mark.it("should return nested endpoint results")
    def test_nested_endpoints(self, mock_run_request, endpoint_node):
        results = endpoint_node.run()

        assert "name" in results
        assert "path" in results

        assert len(list(results["endpoint_results"])) == 2
        assert len(list(results["request_results"])) == 0

        foo_endpoint_result = next(results["endpoint_results"])

        assert "name" in foo_endpoint_result
        assert "path" in foo_endpoint_result

        assert len(list(foo_endpoint_result["endpoint_results"])) == 0
        assert len(list(foo_endpoint_result["request_results"])) == 2

    @mark.context("when there are no nested endpoints")
    @mark.it("should return no nested endpoint results")
    def test_flat_endpoint(self, mock_run_request, flat_endpoint_node):
        results = flat_endpoint_node.run()

        assert "name" in results
        assert "path" in results

        assert len(list(results["endpoint_results"])) == 0
        assert len(list(results["request_results"])) == 2

    @mark.context("when requests are successful")
    @mark.it("should return the responses of the requests")
    def test_when_requests_are_successful(
        self, mock_run_request, endpoint_node
    ):
        mock_run_request.side_effect = ["foo", "bar"]

        results = endpoint_node.run()

        foo_endpoint_results = next(results["endpoint_results"])
        request_results = list(foo_endpoint_results["request_results"])

        assert len(request_results) == 2

        assert request_results == ["foo", "barr"]

    @mark.context("when there is an error during a request")
    @mark.it("should log the error and change session exit code")
    def test_when_request_fails(
        self, mock_run_request, mock_session, caplog, endpoint_node
    ):
        mock_run_request.side_effect = ["foo", HTTPError("error: bar")]
        with caplog.at_level(logging.ERROR):
            results = endpoint_node.run()
            foo_endpoint_results = next(results["endpoint_results"])
            request_results = list(foo_endpoint_results["request_results"])

        assert len(request_results) == 1

        assert (
            "\nError to make request 'http://foo.com/second'. \nerror: bar\n"
            in caplog.text
        )

        assert mock_run_request.call_count == 2

        assert mock_session.exit_code == ExitCode.REQUEST_ERROR
