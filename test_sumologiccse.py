
import json
import sys
import time
import logging
import re
import os
from sumologiccse.sumologiccse import SumoLogicCSE

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel('INFO')

from sumologiccse.sumologiccse import SumoLogicCSE
cse=SumoLogicCSE(endpoint='https://long-api.sumologic.net/api/sec')
q = '-status:"closed"'
#i = cse.get_insights(q=q)
i = cse.get_insights_list(q=q,limit=1)

class Test_Session:
    def test_run(self):
        assert 1 == 1

    def test_session_has_endpoint(self):
        assert re.match('https://.+sumologic.+/sec',cse.endpoint)

class Test_Insights:
    def get_insight_returns_insight(self):
        logger.info(f"get_insight:{i[0]['readableId']}")
        assert re.match('INSIGHT-[0-9]+',cse.get_insight(i[0]['id'])[0]['readableId'])

    def test_get_insights_returns_insight(self):
        q = '-status:"closed"'
        insights = cse.get_insights(q=q)
        assert len(insights)>0 and re.match('INSIGHT-[0-9]+',insights[0]['readableId'])
    
    def test_get_insights_list_returns_list(self):
        insights = cse.get_insights_list(q=q)
        assert len(insights['data']['objects']) > 0 and re.match('INSIGHT-[0-9]+',insights['data']['objects'][0]['readableId'])

    def test_query_insights_returns_one_item(self):
        insights = cse.query_insights(q=None,offset=0,limit=1)
        assert len(insights) == 1

    def test_query_insights_returns_ten_items(self):
        insights = cse.query_insights(q=None,offset=0,limit=10)
        assert len(insights) == 10

    def test_query_insights_returns_100_items(self):
        insights = cse.query_insights(q=None,offset=0,limit=100)
        assert len(insights) == 100
