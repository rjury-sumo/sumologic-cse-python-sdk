import argparse
import json
import logging
import os
import re
from datetime import datetime, timedelta

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel("INFO")

parser = argparse.ArgumentParser(
    description="Changes the status and resolution state of a list of CSE insights using a search query, and adds a comment to each for audit. Runs in dry-run mode by default (use --no-dryrun to execute changes). To avoid param error use: --query='-status:\"closed\"'"
)
parser.add_argument(
    "--accessid",
    help="access id (default: SUMO_ACCESS_KEY)",
    default=os.environ.get("SUMO_ACCESS_ID"),
)
parser.add_argument(
    "--accesskey",
    help="access key (default: SUMO_ACCESS_KEY",
    default=os.environ.get("SUMO_ACCESS_KEY"),
)
parser.add_argument(
    "--endpoint", help="specify an endpoint (default: us2)", default="us2"
)
parser.add_argument(
    "--query",
    help='q param to select insights to close in DSL format. To avoid param error use: --query=\'-status:"closed"\' (default: -status:"closed" readableId:"INSIGHT-20505")',
    default='-status:"closed" readableId:"INSIGHT-20505"',
)
parser.add_argument(
    "--resolution",
    help="resolution to add to closed insight sauch as: No Action, False Positive, Duplicate, Resolved (default: False Postive)",
    default="False Positive",
)
parser.add_argument(
    "--no-dryrun",
    help="Actually execute changes (by default script runs in dry-run mode).",
    dest="dryrun",
    action="store_false",
    default=True,
)
parser.add_argument(
    "--confidence",
    help="Max confidence score to close on. (Default 1)",
    default=1,
    type=int,
)
parser.add_argument(
    "--daysold",
    help="Days ago to delete before. Such as created < 14 days ago. Use 0 for all time. (Default 14)",
    default=14,
    type=int,
)
parser.add_argument(
    "--limit", help="Max insights to close (default 50)", default=1, type=int
)
parser.add_argument(
    "--status", help="Status to close to typically (Default closed)", default="closed"
)
parser.add_argument(
    "--comment",
    help="Comment to add to closed insights.",
    default="Closed via API",
    type=str,
)
parser.add_argument(
    "--filterregex",
    help="A client side filter regular expresssion evaluated again a json dump of the insight recor. Will include ONLY json insight format that matches this expression.",
    default=".*",
    type=str,
)
args = parser.parse_args()

logger.debug(f"Dict format: {vars(args)}")

from sumologiccse import SumoLogicCSE, AuthenticationError, ConfigurationError

try:
    cse = SumoLogicCSE(
        endpoint=args.endpoint, accessId=args.accessid, accessKey=args.accesskey
    )
    logger.info(f"Successfully connected to endpoint: {args.endpoint}")
except AuthenticationError as e:
    logger.error(f"Authentication failed: {e}")
    logger.error("Please check your SUMO_ACCESS_ID and SUMO_ACCESS_KEY environment variables")
    exit(1)
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
    exit(1)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    exit(1)

# get relative datetime
from datetime import timezone
timenow = datetime.now()
timenowtuc = datetime.now(timezone.utc)
timethen = timenowtuc - timedelta(days=args.daysold)
qstarttime = timethen.strftime("%Y-%m-%dT%H:%M:%S") + "+00:00"
if args.daysold > 0:
    q = args.query + f" created:<{qstarttime}"
else:
    q = args.query

# if args.comment == None:
#     comment=f"Closed by API from host: {os.uname().nodename} at {datetime.now()}"
# else:
comment = args.comment
mode = "DRY-RUN MODE (no changes will be made)" if args.dryrun else "EXECUTION MODE (changes will be made)"
logger.info(f"Starting query: {q}")
logger.info(f"Running in: {mode}")
insights = cse.query_insights(q=q, limit=args.limit)
if len(insights) > 0:
    filtered_insights = list(
        filter(
            lambda d: d["confidence"] is None or d["confidence"] <= args.confidence,
            insights,
        )
    )
    sorted_insights = sorted(filtered_insights, key=lambda x: x["created"])
    logger.info(f"query matches: {len(insights)} insights. ")
    logger.info(f"after confidence filter: {len(sorted_insights)}")
    # Process insights (dry-run by default, use --no-dryrun to execute)
    n = 0
    for i in sorted_insights:
        n += 1
        if n <= args.limit:
            row = {
                "id": i["id"],
                "readableId": i["readableId"],
                "confidence": str(i["confidence"]),
                "created": i["created"],
                "status": i["status"]["name"],
            }
            json_row = json.dumps(i)
            # logger.debug(json_row)
            # logger.debug("regex:" + args.filterregex)
            if re.search(args.filterregex, json_row):
                logger.info(json.dumps(row))

                if args.dryrun:
                    logger.info(f"[DRY-RUN] Would close: {i['readableId']} with resolution: {args.resolution}")
                    logger.info(f"[DRY-RUN] Would add comment: {comment}")
                else:
                    logger.info(f"Closing: {i['readableId']} with resolution: {args.resolution}")
                    c = cse.add_insight_comment(i["id"], comment)
                    r = cse.update_insight_resolution_status(
                        i["id"], args.resolution, args.status
                    )
                    logger.info(f"Successfully closed: {i['readableId']}")

            else:
                logger.info(
                    "FILTER: filterregex: "
                    + str(args.filterregex)
                    + " does not match json dump of "
                    + i["readableId"]
                )

        else:
            logger.warning(f"Max limit reached of:{args.limit}")
            break
else:
    logger.info(f"No matching insights were found to update for query: {q}")
