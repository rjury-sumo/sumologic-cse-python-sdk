
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

class Test_Session:
    def test_run(self):
        assert 1 == 1

    def test_session_has_endpoint(self):
        assert re.match('https://api.+sumologic.com/api/sec',cse.endpoint)
