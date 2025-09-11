import os

import pytest

from sumologiccse import SumoLogicCSE


class TestDefaultSession:
    def test_run(self):
        assert 1 == 1

    def test_session_default_endpoint(self):
        # Test with dummy credentials to avoid None values
        cse = SumoLogicCSE(accessId="test", accessKey="test")
        assert cse.endpoint == "https://api.sumologic.com/api/sec"

    def test_session_au_endpoint(self):
        cse = SumoLogicCSE(accessId="test", accessKey="test", endpoint="au")
        assert cse.endpoint == "https://api.au.sumologic.com/api/sec"

    def test_session_us2_endpoint(self):
        cse = SumoLogicCSE(accessId="test", accessKey="test", endpoint="us2")
        assert cse.endpoint == "https://api.us2.sumologic.com/api/sec"

    def test_session_prod_endpoint(self):
        cse = SumoLogicCSE(accessId="test", accessKey="test", endpoint="prod")
        assert cse.endpoint == "https://api.sumologic.com/api/sec"

    def test_session_us1_endpoint(self):
        cse = SumoLogicCSE(accessId="test", accessKey="test", endpoint="us1")
        assert cse.endpoint == "https://api.sumologic.com/api/sec"


@pytest.mark.integration
class TestRulesIntegration:
    """Integration tests for rules API methods - requires valid credentials."""

    @pytest.fixture(scope="class", autouse=True)
    def setup_client(self, request):
        """Set up test client with real credentials."""
        access_id = os.getenv("SUMO_ACCESS_ID")
        access_key = os.getenv("SUMO_ACCESS_KEY")
        endpoint = "au"

        if not access_id or not access_key:
            pytest.skip(
                "Integration tests require SUMO_ACCESS_ID and SUMO_ACCESS_KEY "
                "environment variables"
            )

        request.cls.cse = SumoLogicCSE(
            accessId=access_id, accessKey=access_key, endpoint=endpoint
        )

    def test_get_rules_basic(self):
        """Test basic get_rules functionality."""
        response = self.cse.get_rules(limit=5)

        # Validate response structure
        assert "data" in response
        assert "objects" in response["data"]
        assert "hasNextPage" in response["data"]
        assert isinstance(response["data"]["objects"], list)

        # Validate rule objects if any exist
        if response["data"]["objects"]:
            rule = response["data"]["objects"][0]
            assert "id" in rule
            assert "name" in rule
            assert rule["id"]  # ID should not be empty

    def test_get_rules_with_query(self):
        """Test get_rules with query filter."""
        response = self.cse.get_rules(q="enabled:true", limit=3)

        assert "data" in response
        assert isinstance(response["data"]["objects"], list)

        # All returned rules should match the query criteria
        for rule in response["data"]["objects"]:
            assert "enabled" in rule
