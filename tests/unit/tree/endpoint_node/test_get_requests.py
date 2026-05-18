from pytest import mark


@mark.describe("endpoint node")
@mark.describe("_get_requests")
class TestGetRequests:
    @mark.context("when node has children")
    @mark.it("should not return children requests")
    def test_when_node_has_children(self, endpoint_node):
        requests = list(endpoint_node._get_requests())
        assert len(requests) == 0

    @mark.context("when node has requests")
    @mark.it("should return only its requests")
    def test_node_has_requests(self, flat_endpoint_node):
        requests = list(flat_endpoint_node._get_requests())
        assert len(requests) == 2
