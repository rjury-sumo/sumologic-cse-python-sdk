import argparse
import json
import logging
import os
import sys

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel("DEBUG")

parser = argparse.ArgumentParser(
    description="Retrieve CSE rules using query filters and display results"
)
parser.add_argument(
    "--accessid",
    help="access id (default: SUMO_ACCESS_ID)",
    default=os.environ.get("SUMO_ACCESS_ID"),
)
parser.add_argument(
    "--accesskey",
    help="access key (default: SUMO_ACCESS_KEY)",
    default=os.environ.get("SUMO_ACCESS_KEY"),
)
parser.add_argument(
    "--endpoint", help="specify an endpoint (default: us2)", default="us2"
)
parser.add_argument(
    "--query",
    help='q param to filter rules in DSL format. Example: --query="enabled:true"',
    default=None,
)
parser.add_argument(
    "--limit", help="Max rules to retrieve (default 50)", default=50, type=int
)
parser.add_argument("--rule-id", help="Get a specific rule by ID", default=None)
args = parser.parse_args()

from sumologiccse.sumologiccse import SumoLogicCSE

cse = SumoLogicCSE(
    endpoint=args.endpoint, accessId=args.accessid, accessKey=args.accesskey
)

if args.rule_id:
    # Get specific rule by ID
    try:
        rule = cse.get_rule(args.rule_id)
        print(json.dumps(rule, indent=2))
    except Exception as e:
        logger.error(f"Error retrieving rule {args.rule_id}: {e}")
        sys.exit(1)
else:
    # Query rules with filters
    rules = cse.query_rules(q=args.query, limit=args.limit)
    logger.info(f"query: {args.query} returned: {len(rules)} rules.")

    # Print rules in a formatted way
    for rule in rules:
        row = {
            "id": rule["id"],
            "name": rule["name"],
            "enabled": rule["enabled"],
            "ruleType": rule["ruleType"],
            "severity": rule.get("severity", "N/A"),
            "created": rule.get("created", "N/A"),
            "createdBy": rule.get("createdBy", "N/A"),
        }
        print(json.dumps(row))

    print(f"\nTotal rules retrieved: {len(rules)}")
