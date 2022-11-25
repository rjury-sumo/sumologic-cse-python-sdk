
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
cse=SumoLogicCSE(endpoint='us2')
q = '-status:"closed"'
i = cse.get_insights(q=q)

class Test_Session:
    def test_run(self):
        assert 1 == 1

    def test_session_has_endpoint(self):
        assert re.match('https://api.+sumologic.com/api/sec',cse.endpoint)

class Test_Insights:
    def get_insight_returns_insight(self):
        logger.info(f"get_insight:{i[0]['readableId']}")
        assert re.match('INSIGHT-[0-9]+',cse.get_insight(i[0]['id'])[0]['readableId'])

    def test_get_insights_returns_insight(self):
        q = '-status:"closed"'
        insights = cse.get_insights(q=q)
        assert len(insights)>0 and re.match('INSIGHT-[0-9]+',insights[0]['readableId'])
