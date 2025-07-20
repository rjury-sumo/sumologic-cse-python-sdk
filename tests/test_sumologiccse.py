import json
import sys
import time
import logging
import re
import os
from sumologiccse.sumologiccse import SumoLogicCSE
import unittest
from unittest.mock import patch, MagicMock

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel('INFO')

cse=SumoLogicCSE(accessId=os.getenv('SUMO_ACCESS_ID_DEMO'), 
                accessKey=os.getenv('SUMO_ACCESS_KEY_DEMO'))

from sumologiccse.sumologiccse import SumoLogicCSE
class Test_Default_Session:
    def test_run(self):
        assert 1 == 1

    def test_session_default_endpoint(self):
        assert 'https://api.sumologic.com/api/sec',SumoLogicCSE().endpoint

    def test_session_au_endpoint(self):
        assert 'https://api.au.sumologic.com/api/sec',SumoLogicCSE(endpoint='au').endpoint

    def test_session_us2_endpoint(self):
        assert 'https://api.us2.sumologic.com/api/sec',SumoLogicCSE(endpoint='us2').endpoint

    def test_session_prod_endpoint(self):
        assert 'https://api.sumologic.com/api/sec',SumoLogicCSE(endpoint='prod').endpoint

    def test_session_us1_endpoint(self):
        assert 'https://api.sumologic.com/api/sec',SumoLogicCSE(endpoint='us1').endpoint
    

class Test_Insights:
    def get_insight_returns_insight(self):
        q = '-status:"closed"'
        insights = cse.get_insights(q=q)
        logger.info(f"get_insight:{i[0]['readableId']}")
        assert re.match('INSIGHT-[0-9]+',cse.get_insight(i[0]['id'])[0]['readableId'])

    def test_get_insights_returns_insight(self):
        q = '-status:"closed"'
        insights = cse.get_insights(q=q)
        assert len(insights)>0 and re.match('INSIGHT-[0-9]+',insights[0]['readableId'])
    
    def test_get_insights_list_returns_list(self):
        q = '-status:"closed"'
        insights = cse.get_insights_list(q=q)
        assert len(insights['data']['objects']) > 0 and re.match('INSIGHT-[0-9]+',insights['data']['objects'][0]['readableId'])

    def test_query_insights_returns_one_item(self):
        insights = cse.query_insights(q=None,offset=0,limit=1)
        assert len(insights) == 1

class TestRulesIntegration(unittest.TestCase):
    """Integration tests for rules API methods - requires valid credentials."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client with real credentials."""
        cls.access_id = os.getenv('SUMO_ACCESS_ID')
        cls.access_key = os.getenv('SUMO_ACCESS_KEY')
        cls.endpoint =  'au'
        
        if not cls.access_id or not cls.access_key:
            raise unittest.SkipTest("Integration tests require SUMO_ACCESS_ID_DEMO and SUMO_ACCESS_KEY_DEMO environment variables")
        
        cls.cse = SumoLogicCSE(
            accessId=cls.access_id,
            accessKey=cls.access_key,
            endpoint=cls.endpoint
        )
    
    def setUp(self):
        """Add delay between tests to avoid rate limiting."""
        time.sleep(0.5)

    def test_get_rules_basic(self):
        """Test basic get_rules functionality."""
        response = self.cse.get_rules(limit=5)
        
        # Validate response structure
        self.assertIn('data', response)
        self.assertIn('objects', response['data'])
        self.assertIn('hasNextPage', response['data'])
        self.assertIsInstance(response['data']['objects'], list)
        
        # Validate rule objects if any exist
        if response['data']['objects']:
            rule = response['data']['objects'][0]
            self.assertIn('id', rule)
            self.assertIn('name', rule)
            self.assertTrue(rule['id'])  # ID should not be empty

    def test_get_rules_with_query(self):
        """Test get_rules with query filter."""
        response = self.cse.get_rules(q='enabled:true', limit=3)
        
        self.assertIn('data', response)
        self.assertIsInstance(response['data']['objects'], list)
        
        # All returned rules should match the query criteria
        for rule in response['data']['objects']:
            self.assertIn('enabled', rule)

