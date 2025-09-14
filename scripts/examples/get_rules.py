#!/usr/bin/env python3
"""
Rules Demo Script

This script demonstrates how to retrieve and work with detection rules
using the Sumo Logic Cloud SIEM Python SDK.

Detection rules define the logic for identifying security threats and
generating signals from normalized log data in Cloud SIEM.
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
    description="Retrieve and display detection rules from Cloud SIEM"
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
    "--query",
    help="Search query to filter rules (e.g., 'authentication', 'mitre')",
    type=str
)
parser.add_argument(
    "--offset",
    help="Offset for pagination (default: 0)",
    type=int,
    default=0
)
parser.add_argument(
    "--limit",
    help="Maximum number of rules to retrieve (default: 20, max: 100)",
    type=int,
    default=20
)
parser.add_argument(
    "--output-format",
    help="Output format: table, json, details, or summary (default: table)",
    choices=["table", "json", "details", "summary"],
    default="table"
)
parser.add_argument(
    "--rule-id",
    help="Get details for a specific rule ID",
    type=str
)
parser.add_argument(
    "--filter-enabled",
    help="Show only enabled rules",
    action="store_true"
)
parser.add_argument(
    "--category",
    help="Filter by rule category/type",
    type=str
)
parser.add_argument(
    "--severity",
    help="Filter by severity level (e.g., 'High', 'Medium', 'Low')",
    type=str
)

args = parser.parse_args()

# Validate limit
if args.limit > 100:
    logger.warning("Limit exceeds maximum of 100, setting to 100")
    args.limit = 100

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

def format_date(date_str):
    """Format ISO date string to readable format."""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return date_str[:10] if len(date_str) > 10 else date_str

def build_search_query():
    """Build search query from command line arguments."""
    query_parts = []

    if args.query:
        query_parts.append(args.query)

    if args.category:
        query_parts.append(f"category:{args.category}")

    if args.severity:
        query_parts.append(f"severity:{args.severity}")

    return " ".join(query_parts) if query_parts else None

def filter_rules(rules):
    """Apply additional filtering to rules."""
    filtered_rules = rules

    if args.filter_enabled:
        filtered_rules = [rule for rule in filtered_rules if rule.get('enabled', False)]

    return filtered_rules

def format_table_output(rules_data):
    """Format rules as a table."""
    rules = rules_data.get('data', {}).get('objects', [])

    if not rules:
        print("No rules found.")
        return

    # Apply additional filtering
    rules = filter_rules(rules)

    if not rules:
        print("No rules found after filtering.")
        return

    # Print header
    print(f"{'ID':<20} {'Name':<35} {'Severity':<8} {'Enabled':<8} {'Created':<12}")
    print("-" * 85)

    for rule in rules:
        # Safely extract fields with defaults
        rule_id = rule.get('id', 'N/A')[:20]
        name = rule.get('name', 'N/A')[:35]
        severity = str(rule.get('severity', 'N/A'))[:8]
        enabled = 'Yes' if rule.get('enabled', False) else 'No'
        created = format_date(rule.get('createdAt'))

        print(f"{rule_id:<20} {name:<35} {severity:<8} {enabled:<8} {created:<12}")

def format_details_output(rules_data):
    """Format rules with detailed information."""
    rules = rules_data.get('data', {}).get('objects', [])

    if not rules:
        print("No rules found.")
        return

    # Apply additional filtering
    rules = filter_rules(rules)

    if not rules:
        print("No rules found after filtering.")
        return

    for i, rule in enumerate(rules):
        if i > 0:
            print("\n" + "="*80)

        print("Detection Rule Details")
        print("="*80)
        print(f"ID: {rule.get('id', 'N/A')}")
        print(f"Name: {rule.get('name', 'N/A')}")
        print(f"Enabled: {'Yes' if rule.get('enabled', False) else 'No'}")
        print(f"Severity: {rule.get('severity', 'N/A')}")

        # Description and summary
        if rule.get('description'):
            print(f"Description: {rule['description']}")

        if rule.get('summary'):
            print(f"Summary: {rule['summary']}")

        # Rule logic and expression
        if rule.get('expression'):
            expression = rule['expression']
            # Truncate very long expressions
            if len(expression) > 200:
                expression = expression[:200] + "..."
            print(f"Expression: {expression}")

        # Entity selectors
        if rule.get('entitySelectors'):
            selectors = rule['entitySelectors']
            if isinstance(selectors, list) and selectors:
                print("Entity Selectors:")
                for selector in selectors[:3]:  # Show first 3 selectors
                    entity_type = selector.get('entityType', 'N/A')
                    expression = selector.get('expression', 'N/A')
                    if len(expression) > 100:
                        expression = expression[:100] + "..."
                    print(f"  - {entity_type}: {expression}")
                if len(selectors) > 3:
                    print(f"  ... and {len(selectors) - 3} more selectors")

        # MITRE ATT&CK information
        if rule.get('tags'):
            tags = rule['tags']
            mitre_tags = [tag for tag in tags if 'mitre' in str(tag).lower() or 'T1' in str(tag)]
            if mitre_tags:
                print(f"MITRE ATT&CK Tags: {', '.join(str(tag) for tag in mitre_tags[:5])}")

        # Rule category/type
        if rule.get('ruleType'):
            print(f"Rule Type: {rule['ruleType']}")

        # Suppression settings
        if rule.get('suppressionWindowSize'):
            print(f"Suppression Window: {rule['suppressionWindowSize']} ms")

        # Stream information
        if rule.get('stream'):
            print(f"Stream: {rule['stream']}")

        # Score and risk information
        if rule.get('score') is not None:
            print(f"Score: {rule['score']}")

        # Window size for aggregation rules
        if rule.get('windowSize'):
            window_size = rule['windowSize']
            if isinstance(window_size, dict):
                window_str = f"{window_size.get('windowSize', 'N/A')} {window_size.get('windowSizeUnit', 'ms')}"
                print(f"Window Size: {window_str}")
            else:
                print(f"Window Size: {window_size}")

        # Ordered fields (for Chain rules)
        if rule.get('ordered'):
            print(f"Ordered: {'Yes' if rule['ordered'] else 'No'}")

        # Audit information
        print(f"Created: {format_date(rule.get('createdAt'))}")
        print(f"Modified: {format_date(rule.get('modifiedAt'))}")
        if rule.get('createdBy'):
            print(f"Created By: {rule['createdBy']}")
        if rule.get('modifiedBy'):
            print(f"Modified By: {rule['modifiedBy']}")

def format_summary_output(rules_data):
    """Format rules summary information."""
    rules = rules_data.get('data', {}).get('objects', [])
    pagination_info = rules_data.get('data', {})

    # Apply additional filtering
    original_count = len(rules)
    rules = filter_rules(rules)

    print("Detection Rules Summary")
    print("="*50)
    print(f"Total rules returned: {original_count}")
    if len(rules) < original_count:
        print(f"Rules after filtering: {len(rules)}")
    print(f"Has next page: {'Yes' if pagination_info.get('hasNextPage', False) else 'No'}")

    if rules:
        # Severity breakdown
        severity_counts = {}
        enabled_count = 0
        rule_types = {}

        for rule in rules:
            severity = rule.get('severity', 'Unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

            if rule.get('enabled', False):
                enabled_count += 1

            rule_type = rule.get('ruleType', 'Unknown')
            rule_types[rule_type] = rule_types.get(rule_type, 0) + 1

        print(f"\nEnabled rules: {enabled_count} of {len(rules)}")

        print("\nBreakdown by Severity:")
        for severity, count in sorted(severity_counts.items()):
            print(f"  {severity}: {count}")

        print("\nBreakdown by Rule Type:")
        for rule_type, count in sorted(rule_types.items()):
            print(f"  {rule_type}: {count}")

def main():
    """Main execution function."""
    try:
        if args.rule_id:
            # Get specific rule by ID
            logger.info(f"Retrieving rule: {args.rule_id}")
            rule_data = cse.get_rule(args.rule_id)

            # Handle response format and show single rule
            if isinstance(rule_data, dict) and 'data' in rule_data:
                rule = rule_data['data']
            else:
                rule = rule_data

            # Create a fake rules_data structure for consistent formatting
            fake_data = {'data': {'objects': [rule]}}

            if args.output_format == "json":
                print(json.dumps(rule, indent=2))
            else:
                format_details_output(fake_data)

        else:
            # Build search query from arguments
            search_query = build_search_query()

            # Build query parameters
            params = {
                'q': search_query,
                'offset': args.offset,
                'limit': args.limit
            }

            # Log request details
            if search_query:
                logger.info(f"Retrieving rules with query: '{search_query}' (offset: {args.offset}, limit: {args.limit})")
            else:
                logger.info(f"Retrieving rules (offset: {args.offset}, limit: {args.limit})")

            # Get rules
            rules_data = cse.get_rules(**{k: v for k, v in params.items() if v is not None})

            # Extract rules and pagination info
            rules = rules_data.get('data', {}).get('objects', [])
            pagination_info = rules_data.get('data', {})

            logger.info(f"Retrieved {len(rules)} rules")

            # Output results based on format
            if args.output_format == "json":
                # Apply filtering before JSON output
                filtered_rules = filter_rules(rules)
                rules_data['data']['objects'] = filtered_rules
                print(json.dumps(rules_data, indent=2))
            elif args.output_format == "details":
                format_details_output(rules_data)
            elif args.output_format == "summary":
                format_summary_output(rules_data)
            else:  # table format
                format_table_output(rules_data)

            # Show pagination info for non-JSON output
            if args.output_format != "json" and args.output_format != "summary":
                print("\nPagination info:")
                print(f"  Offset: {args.offset}")
                print(f"  Limit: {args.limit}")
                print(f"  Has next page: {'Yes' if pagination_info.get('hasNextPage', False) else 'No'}")

                if pagination_info.get('hasNextPage'):
                    next_offset = args.offset + args.limit
                    print(f"  Next page offset: {next_offset}")
                    print(f"  Use: --offset {next_offset} to get next page")

                # Show applied filters
                filters_applied = []
                if args.filter_enabled:
                    filters_applied.append("enabled only")
                if search_query:
                    filters_applied.append(f"query: '{search_query}'")

                if filters_applied:
                    print(f"  Filters applied: {', '.join(filters_applied)}")

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

