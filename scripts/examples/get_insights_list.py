#!/usr/bin/env python3
"""
Insights List Demo Script

This script demonstrates how to retrieve insights using the get_insights_list endpoint
of the Sumo Logic Cloud SIEM Python SDK.

The get_insights_list endpoint provides a simple list view of insights with
offset and limit pagination, ideal for basic listing and browsing operations.
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
    description="Retrieve insights list from Cloud SIEM"
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
    help="Search query to filter insights",
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
    help="Maximum number of insights to retrieve (default: 20, max: 100)",
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
    "--show-closed",
    help="Include closed insights in results",
    action="store_true"
)
parser.add_argument(
    "--show-signals",
    help="Show signal information in details view",
    action="store_true"
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
        return dt.strftime('%Y-%m-%d %H:%M')
    except (ValueError, TypeError):
        return date_str[:16] if len(date_str) > 16 else date_str

def format_table_output(insights_data):
    """Format insights as a table."""
    insights = insights_data.get('data', {}).get('objects', [])

    if not insights:
        print("No insights found.")
        return

    # Print header
    print(f"{'ID':<20} {'Name':<30} {'Severity':<8} {'Status':<12} {'Updated':<16}")
    print("-" * 88)

    for insight in insights:
        # Safely extract fields with defaults
        insight_id = insight.get('id', 'N/A')[:20]
        name = insight.get('name', 'N/A')[:30]
        severity = insight.get('severity', 'N/A')[:8]
        status = insight.get('status', {}).get('displayName', 'N/A')[:12]
        updated = format_date(insight.get('lastUpdated'))

        print(f"{insight_id:<20} {name:<30} {severity:<8} {status:<12} {updated:<16}")

def format_details_output(insights_data):
    """Format insights with detailed information."""
    insights = insights_data.get('data', {}).get('objects', [])

    if not insights:
        print("No insights found.")
        return

    for i, insight in enumerate(insights):
        if i > 0:
            print("\n" + "="*80)

        print("Insight Details")
        print("="*80)
        print(f"ID: {insight.get('id', 'N/A')}")
        print(f"Name: {insight.get('name', 'N/A')}")
        print(f"Description: {insight.get('description', 'N/A')}")
        print(f"Severity: {insight.get('severity', 'N/A')}")

        # Status information
        status_info = insight.get('status', {})
        if status_info:
            print(f"Status: {status_info.get('displayName', 'N/A')}")

        # Assignment information
        assignee = insight.get('assignee')
        if assignee:
            assignee_name = assignee.get('username', assignee.get('email', 'N/A'))
            print(f"Assignee: {assignee_name}")
        else:
            print("Assignee: Unassigned")

        # Entity information
        entity = insight.get('entity')
        if entity:
            entity_name = entity.get('hostname', entity.get('value', 'N/A'))
            entity_type = entity.get('entityType', 'N/A')
            print(f"Entity: {entity_name} ({entity_type})")

        # Signal information (if requested)
        if args.show_signals:
            signals = insight.get('signals', [])
            if signals:
                print(f"Signals ({len(signals)} total):")
                for signal in signals[:5]:  # Show first 5 signals
                    signal_name = signal.get('name', 'N/A')
                    signal_stage = signal.get('stage', 'N/A')
                    signal_severity = signal.get('severity', 'N/A')
                    print(f"  - {signal_name} (Stage: {signal_stage}, Severity: {signal_severity})")
                if len(signals) > 5:
                    print(f"  ... and {len(signals) - 5} more signals")
            else:
                print("Signals: None")

        # Tags
        tags = insight.get('tags')
        if tags:
            if isinstance(tags, list):
                print(f"Tags: {', '.join(str(tag) for tag in tags)}")
            else:
                print(f"Tags: {tags}")

        # Timestamps
        print(f"Created: {format_date(insight.get('created'))}")
        print(f"Last Updated: {format_date(insight.get('lastUpdated'))}")

        # Closed information
        if insight.get('closed'):
            print(f"Closed: {format_date(insight.get('closed'))}")
            if insight.get('closedBy'):
                print(f"Closed By: {insight['closedBy']}")

def format_summary_output(insights_data):
    """Format insights summary information."""
    insights = insights_data.get('data', {}).get('objects', [])
    pagination_info = insights_data.get('data', {})

    print("Insights Summary")
    print("="*50)
    print(f"Total insights returned: {len(insights)}")
    print(f"Has next page: {'Yes' if pagination_info.get('hasNextPage', False) else 'No'}")

    if insights:
        # Severity breakdown
        severity_counts = {}
        status_counts = {}
        assignee_counts = {}

        for insight in insights:
            severity = insight.get('severity', 'Unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

            status = insight.get('status', {}).get('displayName', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

            assignee = insight.get('assignee')
            if assignee:
                assignee_name = assignee.get('username', assignee.get('email', 'N/A'))
                assignee_counts[assignee_name] = assignee_counts.get(assignee_name, 0) + 1
            else:
                assignee_counts['Unassigned'] = assignee_counts.get('Unassigned', 0) + 1

        print("\nBreakdown by Severity:")
        for severity, count in sorted(severity_counts.items()):
            print(f"  {severity}: {count}")

        print("\nBreakdown by Status:")
        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count}")

        print("\nBreakdown by Assignee:")
        top_assignees = sorted(assignee_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for assignee, count in top_assignees:
            print(f"  {assignee}: {count}")
        if len(assignee_counts) > 5:
            print(f"  ... and {len(assignee_counts) - 5} more assignees")

def main():
    """Main execution function."""
    try:
        # Build query parameters
        params = {
            'q': args.query,
            'offset': args.offset,
            'limit': args.limit
        }

        # Log request details
        if args.query:
            logger.info(f"Retrieving insights list with query: '{args.query}' (offset: {args.offset}, limit: {args.limit})")
        else:
            logger.info(f"Retrieving insights list (offset: {args.offset}, limit: {args.limit})")

        # Get insights list
        insights_data = cse.get_insights_list(**{k: v for k, v in params.items() if v is not None})

        # Extract insights and pagination info
        insights = insights_data.get('data', {}).get('objects', [])
        pagination_info = insights_data.get('data', {})

        logger.info(f"Retrieved {len(insights)} insights")

        # Filter out closed insights if not requested
        if not args.show_closed:
            original_count = len(insights)
            insights = [i for i in insights if not i.get('closed')]
            if len(insights) < original_count:
                logger.info(f"Filtered out {original_count - len(insights)} closed insights")
                # Update the data structure for output functions
                insights_data['data']['objects'] = insights

        # Output results based on format
        if args.output_format == "json":
            print(json.dumps(insights_data, indent=2))
        elif args.output_format == "details":
            format_details_output(insights_data)
        elif args.output_format == "summary":
            format_summary_output(insights_data)
        else:  # table format
            format_table_output(insights_data)

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

