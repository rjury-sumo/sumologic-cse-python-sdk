import argparse, sys
import json
import sys
import time
import logging
import os
import time; 
import math
import re
from datetime import datetime
from datetime import timedelta

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel('INFO')

parser=argparse.ArgumentParser(description="Changes the status and resolution state of a list of CSE insights using a search query, and adds a comment to each for audit. To avoid param error use: --query=\'-status:\"closed\"\'")
parser.add_argument("--accessid", help="access id (default: SUMO_ACCESS_KEY)", default=os.environ.get('SUMO_ACCESS_ID'))
parser.add_argument("--accesskey", help='access key (default: SUMO_ACCESS_KEY', default=os.environ.get('SUMO_ACCESS_KEY'))
parser.add_argument("--endpoint", help="specify an endpoint (default: us2)", default='https://api.us2.sumologic.com/api/sec')
parser.add_argument("--query", help='q param to select insights to close in DSL format. To avoid param error use: --query=\'-status:\"closed\"\' (default: -status:"closed" readableId:"INSIGHT-20505")', default='-status:"closed" readableId:"INSIGHT-20505"')
parser.add_argument("--resolution", help="resolution to add to closed insight sauch as: No Action, False Positive, Duplicate, Resolved (default: False Postive)", default='False Positive')
parser.add_argument("--dryrun", help="Default true to show only. Set to False to close matching insights. (default: False)", default=False)
parser.add_argument("--confidence", help="Max confidence score to close on. (Default 1)", default=1, type=int)
parser.add_argument("--daysold", help="Days ago to delete before. Such as created < 14 days ago. Use 0 for all time. (Default 14)", default=14, type=int)
parser.add_argument("--limit", help="Max insights to close (default 50)", default=50, type=int)
parser.add_argument("--status", help="Status to close to typically (Default closed)", default='closed')
parser.add_argument("--comment", help="Comment to add to closed insights.", default="Closed via API", type=str)
parser.add_argument("--filterregex", help="A client side filter regular expresssion evaluated again a json dump of the insight recor. Will include ONLY json insight format that matches this expression.", default=".*", type=str)
args=parser.parse_args()

logger.debug(f"Dict format: {vars(args)}")

from sumologiccse.sumologiccse import SumoLogicCSE
cse=SumoLogicCSE(endpoint=args.endpoint)

# get relative datetime
timenow=datetime.now
timenowtuc= datetime.utcnow()
timethen=timenowtuc - timedelta(days=args.daysold)
qstarttime=timethen.strftime("%Y-%m-%dT%H:%M:%S") + '+00:00'
q = args.query + f" created:<{qstarttime}"

# if args.comment == None:
#     comment=f"Closed by API from host: {os.uname().nodename} at {datetime.now()}"
# else:
comment= args.comment

insights = cse.query_insights(q=q,limit=args.limit)
if len(insights) > 0:
    filtered_insights = list(filter(lambda d: d['confidence'] == None or d['confidence'] <= args.confidence, insights))
    sorted_insights = sorted(filtered_insights, key=lambda x: x['created'])
    logger.info(f"query: {q} found: {len(insights)} insights. dryrun: {args.dryrun}")
    logger.info(f"after confidence filter: {len(sorted_insights)}")
    # set dryrun to False to do status update
    n=0
    for i in sorted_insights:
        n+=1
        if n <= args.limit:
            row = {
                'id': i['id'],
                'readableId': i['readableId'],
                'confidence': str(i['confidence']),
                'created': i['created'],
                'status': i['status']['name']
                }
            json_row=json.dumps(i)
            #logger.debug(json_row)
            #logger.debug("regex:" + args.filterregex)
            if re.search(args.filterregex,json_row):
                logger.info(json.dumps(row))

                if args.dryrun == False:
                    logger.info(f"Closing: {i['readableId']} with resolution: {args.resolution}")
                    c = cse.add_insight_comment(i['id'],comment)
                    r = cse.update_insight_resolution_status(i['id'],args.resolution,args.status)
            else:
                logger.info("FILTER: filterregex: " + str(args.filterregex) + " does not match json dump of " + i['readableId'])

        else:
            logger.warning(f"Max limit reached of:{args.limit}" )
            break
else:
    logger.info(f"No matching insights were found to update for query: {q}")