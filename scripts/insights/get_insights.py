import json
import sys
import time
import logging
import os

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel('INFO')

from sumologiccse.sumologiccse import SumoLogicCSE
cse=SumoLogicCSE(endpoint='us2')

# examples of DSL - to get more try copying from urldecoded url in insights UI page
#q = 'readableId:"INSIGHT-20190"'
#q = 'status:"new"'
# everything
#q = None
# status is not closed and created before date 
q = '-status:"closed" created:>2022-11-17T00:00:00+00:00'

insights = cse.get_insights(q=q)
logger.info('query: + ' + str(q) + ' returned: ' + str(len(insights)) + ' insights.')

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