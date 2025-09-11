#!/usr/bin/env python3
"""
Rule Tuning Expressions Demo Script

This script demonstrates how to retrieve and work with rule tuning expressions
using the Sumo Logic Cloud SIEM Python SDK.

Rule tuning expressions allow you to modify rule behavior without editing the rule directly,
providing fine-grained control over when rules should trigger.
"""

import argparse
import json
import logging
import os
from datetime import datetime

from sumologiccse import APIError, AuthenticationError, ConfigurationError, SumoLogicCSE

# Configure logging
logger = logging.getLogger()
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
    level=logging.INFO
)

# Parse command line arguments
parser = argparse.ArgumentParser(
    description="Retrieve and display rule tuning expressions from Cloud SIEM"
)
parser.add_argument(
    "--accessid",
    help="Sumo Logic access ID (default: SUMO_ACCESS_ID env var)",
    default=os.environ.get("SUMO_ACCESS_ID"),
)
parser.add_argument(
    "--accesskey",
    help="Sumo Logic access key (default: SUMO_ACCESS_KEY env var)",
    default=os.environ.get("SUMO_ACCESS_KEY"),
)
parser.add_argument(
    "--endpoint",
    help="Sumo Logic endpoint (default: us2)",
    default="us2"
)
parser.add_argument(
    "--limit",
    help="Maximum number of rule tuning expressions to retrieve (default: 100)",
    type=int,
    default=100
)
parser.add_argument(
    "--output-format",
    help="Output format: table, json, or summary (default: table)",
    choices=["table", "json", "summary"],
    default="table"
)
parser.add_argument(
    "--filter-enabled",
    help="Show only enabled rule tuning expressions",
    action="store_true"
)

args = parser.parse_args()

# Initialize SDK client
try:
    cse = SumoLogicCSE(
        endpoint=args.endpoint,
        accessId=args.accessid,
        accessKey=args.accesskey
    )
    logger.info(f"Successfully connected to Cloud SIEM endpoint: {args.endpoint}")
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

def format_table_output(expressions):
    """Format rule tuning expressions as a table."""
    if not expressions:
        print("No rule tuning expressions found.")
        return

    # Print header
    print(f"{'ID':<20} {'Name':<40} {'Enabled':<8} {'Rule Name':<30} {'Created':<12}")
    print("-" * 110)

    for expr in expressions:
        # Safely extract fields with defaults
        expr_id = expr.get('id', 'N/A')[:20]
        name = expr.get('name', 'N/A')[:40]
        enabled = 'Yes' if expr.get('enabled', False) else 'No'
        rule_name = expr.get('ruleName', 'N/A')[:30]
        created = expr.get('createdAt', 'N/A')

        # Format creation date
        if created != 'N/A':
            try:
                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                created = created_dt.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                created = created[:12]

        print(f"{expr_id:<20} {name:<40} {enabled:<8} {rule_name:<30} {created:<12}")

def format_summary_output(expressions):
    """Format rule tuning expressions as a summary."""
    if not expressions:
        print("No rule tuning expressions found.")
        return

    total_count = len(expressions)
    enabled_count = sum(1 for expr in expressions if expr.get('enabled', False))
    disabled_count = total_count - enabled_count

    print("\n=== Rule Tuning Expressions Summary ===")
    print(f"Total Expressions: {total_count}")
    print(f"Enabled: {enabled_count}")
    print(f"Disabled: {disabled_count}")
    print()

    # Group by rule if available
    rule_groups = {}
    for expr in expressions:
        rule_name = expr.get('ruleName', 'Unknown Rule')
        if rule_name not in rule_groups:
            rule_groups[rule_name] = []
        rule_groups[rule_name].append(expr)

    print("Expressions by Rule:")
    for rule_name, rule_expressions in rule_groups.items():
        enabled_in_rule = sum(1 for e in rule_expressions if e.get('enabled', False))
        print(f"  {rule_name}: {len(rule_expressions)} expressions ({enabled_in_rule} enabled)")

def main():
    """Main execution function."""
    try:
        logger.info(f"Retrieving rule tuning expressions (limit: {args.limit})")

        # Get all rule tuning expressions
        expressions_data = cse.get_rule_tuning_expressions(limit=args.limit)

        # Extract the expressions array from the response
        if isinstance(expressions_data, dict) and 'data' in expressions_data:
            if 'objects' in expressions_data['data']:
                expressions = expressions_data['data']['objects']
            else:
                expressions = expressions_data['data']
        else:
            expressions = expressions_data if isinstance(expressions_data, list) else []

        logger.info(f"Retrieved {len(expressions)} rule tuning expressions")

        # Apply filtering if requested
        if args.filter_enabled:
            expressions = [expr for expr in expressions if expr.get('enabled', False)]
            logger.info(f"Filtered to {len(expressions)} enabled expressions")

        # Output results based on format
        if args.output_format == "json":
            print(json.dumps(expressions, indent=2))
        elif args.output_format == "summary":
            format_summary_output(expressions)
        else:  # table format
            format_table_output(expressions)

        # Show additional details if we have expressions
        if expressions and args.output_format != "json":
            print(f"\nTotal: {len(expressions)} rule tuning expressions")
            if args.filter_enabled:
                print("(Showing only enabled expressions)")

    except AuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        logger.error("Please verify your credentials and endpoint")
        exit(1)
    except APIError as e:
        logger.error(f"API request failed: {e}")
        if hasattr(e, 'status_code'):
            logger.error(f"HTTP Status Code: {e.status_code}")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main()

