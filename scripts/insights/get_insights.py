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

q = 'readableId:"INSIGHT-20190"'
q = 'status:"new"'
#q = None
insights = cse.get_insights(q=q)
logger.info('query: + ' + str(q) + ' returned: ' + str(len(insights)) + ' insights.')

# print('for example:')
# print (insights[0])

# this is example of filtering client side
filtered_insights = list(filter(lambda d: d['confidence'] == None or d['confidence'] < .9, insights))

for i in filtered_insights:
   print ('id:' + i['readableId'] + ' confidence: ' + str(i['confidence']))
   print(json.dumps(i))