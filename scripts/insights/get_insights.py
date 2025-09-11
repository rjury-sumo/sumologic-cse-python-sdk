import argparse
import json
import logging
import os

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel("DEBUG")

parser = argparse.ArgumentParser(
    description="Changes the status and resolution state of a list of CSE insights using a search query, and adds a comment to each for audit. To avoid param error use: --query='-status:\"closed\"'"
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
    default='-status:"closed"',
)
parser.add_argument(
    "--limit", help="Max insights to close (default 50)", default=50, type=int
)
args = parser.parse_args()

# Debug info
logger.debug(f"Access ID provided: {'Yes' if args.accessid else 'No'}")
logger.debug(f"Access Key provided: {'Yes' if args.accesskey else 'No'}")
logger.debug(f"Endpoint: {args.endpoint}")

from sumologiccse import SumoLogicCSE, AuthenticationError, APIError, ConfigurationError

try:
    cse = SumoLogicCSE(
        endpoint=args.endpoint, accessId=args.accessid, accessKey=args.accesskey
    )
    logger.info(f"Successfully connected to endpoint: {args.endpoint}")
except AuthenticationError as e:
    logger.error(f"Authentication failed: {e}")
    logger.error(
        "Please check your SUMO_ACCESS_ID and SUMO_ACCESS_KEY environment variables"
    )
    logger.error("Or provide --accessid and --accesskey arguments")
    exit(1)
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
    exit(1)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    exit(1)

# examples of DSL - to get more try copying from urldecoded url in insights UI page
# q = 'readableId:"INSIGHT-20190"'
# q = 'status:"new"'
# everything
# q = None
# status is not closed and created before date


try:
    logger.info(f"Querying insights with: {args.query}")
    insights = cse.query_insights(q=args.query, limit=args.limit)
    logger.info(f"Query '{args.query}' returned {len(insights)} insights")
except AuthenticationError as e:
    logger.error(f"Authentication failed during query: {e}")
    logger.error("Possible causes:")
    logger.error("1. Credentials may have expired")
    logger.error("2. Account may not have Cloud SIEM access")
    logger.error(
        "3. Wrong endpoint - try different endpoint (--endpoint prod/us1/us2/au/etc)"
    )
    exit(1)
except APIError as e:
    logger.error(f"API request failed: {e}")
    if hasattr(e, "status_code"):
        logger.error(f"HTTP Status Code: {e.status_code}")
    exit(1)
except Exception as e:
    logger.error(f"Unexpected error during query: {e}")
    exit(1)

# print('for example:')
# print (insights[0])

# this is example of filtering client side
filtered_insights = list(
    filter(lambda d: d["confidence"] is None or d["confidence"] < 0.9, insights)
)

for i in filtered_insights:
    row = {
        "id": i["id"],
        "readableId": i["readableId"],
        "confidence": str(i["confidence"]),
        "created": i["created"],
        "status": i["status"]["name"],
    }
    print(json.dumps(row))
