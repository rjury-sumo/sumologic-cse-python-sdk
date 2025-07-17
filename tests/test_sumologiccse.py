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

    # def test_query_insights_returns_ten_items(self):
    #     insights = cse.query_insights(q=None,offset=0,limit=10)
    #     assert len(insights) == 10

    # def test_query_insights_returns_100_items(self):
    #     insights = cse.query_insights(q=None,offset=0,limit=100)
    #     assert len(insights) == 100

# class TestSumoLogicCSE(unittest.TestCase):

#     @patch('sumologiccse.sumologiccse.requests.Session')
#     def setUp(self, MockSession):
#         self.mock_session = MockSession.return_value
#         self.mock_session.get.return_value = MagicMock(status_code=200, url='https://api.test.sumologic.com/api/sec')
#         self.sumo = SumoLogicCSE(accessId='test_id', accessKey='test_key', endpoint='test')

#     def test_get_versioned_endpoint(self):
#         version = 'v2'
#         expected_endpoint = 'https://api.test.sumologic.com/api/sec/v2'
#         self.assertEqual(self.sumo.get_versioned_endpoint(version), expected_endpoint)

#     def test_delete(self):
#         self.mock_session.delete.return_value = MagicMock(status_code=200)
#         response = self.sumo.delete('/test')
#         self.assertEqual(response.status_code, 200)

#     def test_get(self):
#         self.mock_session.get.return_value = MagicMock(status_code=200, text='{"key": "value"}')
#         response = self.sumo.get('/test')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json(), {"key": "value"})

#     def test_post(self):
#         self.mock_session.post.return_value = MagicMock(status_code=200, text='{"key": "value"}')
#         response = self.sumo.post('/test', params={"param": "value"})
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json(), {"key": "value"})

#     def test_post_file(self):
#         with patch('builtins.open', unittest.mock.mock_open(read_data=b'data')) as mock_file:
#             with patch('sumologiccse.sumologiccse.requests.post') as mock_post:
#                 mock_post.return_value = MagicMock(status_code=200, text='{"key": "value"}')
#                 response = self.sumo.post_file('/test', params={"full_file_path": "path", "file_name": "file", "merge": True})
#                 self.assertEqual(response.status_code, 200)
#                 self.assertEqual(response.json(), {"key": "value"})

#     def test_put(self):
#         self.mock_session.put.return_value = MagicMock(status_code=200, text='{"key": "value"}')
#         response = self.sumo.put('/test', params={"param": "value"})
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json(), {"key": "value"})

#     def test_get_insights_all(self):
#         self.mock_session.get.return_value = MagicMock(status_code=200, text='{"data": {"objects": [], "nextPageToken": null}}')
#         response = self.sumo.get_insights_all()
#         self.assertEqual(response, {"data": {"objects": [], "nextPageToken": None}})

#     def test_get_insights(self):
#         self.mock_session.get.return_value = MagicMock(status_code=200, text='{"data": {"objects": [], "nextPageToken": null}}')
#         response = self.sumo.get_insights()
#         self.assertEqual(response, [])

#     def test_get_insight(self):
#         self.mock_session.get.return_value = MagicMock(status_code=200, text='{"key": "value"}')
#         response = self.sumo.get_insight('test_id')
#         self.assertEqual(response, {"key": "value"})

#     def test_get_insight_statuses(self):
#         self.mock_session.get.return_value = MagicMock(status_code=200, text='{"key": "value"}')
#         response = self.sumo.get_insight_statuses()
#         self.assertEqual(response, {"key": "value"})

#     def test_update_insight_resolution_status(self):
#         self.mock_session.put.return_value = MagicMock(status_code=200, text='{"key": "value"}')
#         response = self.sumo.update_insight_resolution_status('test_id', 'resolved', 'closed')
#         self.assertEqual(response, {"key": "value"})

#     def test_add_insight_comment(self):
#         self.mock_session.post.return_value = MagicMock(status_code=200, text='{"key": "value"}')
#         response = self.sumo.add_insight_comment('test_id', 'test comment')
#         self.assertEqual(response, {"key": "value"})

# if __name__ == '__main__':
#     unittest.main()
