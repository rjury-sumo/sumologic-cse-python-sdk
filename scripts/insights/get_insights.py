import argparse, sys
import json
import sys
import time
import logging
import os
import time; 
import math
from datetime import datetime
from datetime import timedelta

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel('DEBUG')

parser=argparse.ArgumentParser(description="Changes the status and resolution state of a list of CSE insights using a search query, and adds a comment to each for audit. To avoid param error use: --query=\'-status:\"closed\"\'")
parser.add_argument("--accessid", help="access id (default: SUMO_ACCESS_KEY)", default=os.environ.get('SUMO_ACCESS_ID'))
parser.add_argument("--accesskey", help='access key (default: SUMO_ACCESS_KEY', default=os.environ.get('SUMO_ACCESS_KEY'))
parser.add_argument("--endpoint", help="specify an endpoint (default: us2)", default='us2')
parser.add_argument("--query", help='q param to select insights to close in DSL format. To avoid param error use: --query=\'-status:\"closed\"\' (default: -status:"closed" readableId:"INSIGHT-20505")', default='-status:"closed"')
parser.add_argument("--limit", help="Max insights to close (default 50)", default=50, type=int)
args=parser.parse_args()

from sumologiccse.sumologiccse import SumoLogicCSE
cse=SumoLogicCSE(endpoint=args.endpoint, 
                 accessId=args.accessid, 
                 accessKey=args.accesskey)

# examples of DSL - to get more try copying from urldecoded url in insights UI page
#q = 'readableId:"INSIGHT-20190"'
#q = 'status:"new"'
# everything
#q = None
# status is not closed and created before date 


insights = cse.query_insights(q=args.query ,limit=args.limit)
logger.info('query: + ' + str(args.query) + ' returned: ' + str(len(insights)) + ' insights.')

# print('for example:')
# print (insights[0])

# this is example of filtering client side
filtered_insights = list(filter(lambda d: d['confidence'] == None or d['confidence'] < .9, insights))

for i in filtered_insights:
    row = {
        'id': i['id'],
        'readableId': i['readableId'],
        'confidence': str(i['confidence']),
        'created': i['created'],
        'status': i['status']['name']
        }
    print(json.dumps(row))