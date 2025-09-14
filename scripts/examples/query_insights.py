#!/usr/bin/env python3
"""
Query Insights Demo Script

This script demonstrates how to query and search insights using the
Sumo Logic Cloud SIEM Python SDK.

The query_insights endpoint allows flexible searching and filtering
of insights with pagination support for handling large result sets.
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
    description="Query and search insights from Cloud SIEM"
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
    help="Search query to filter insights (e.g., 'High' for high severity)",
    type=str
)
parser.add_argument(
    "--limit",
    help="Maximum number of insights to retrieve (default: 50)",
    type=int,
    default=50
)
parser.add_argument(
    "--output-format",
    help="Output format: table, json, or details (default: table)",
    choices=["table", "json", "details"],
    default="table"
)
parser.add_argument(
    "--status",
    help="Filter by insight status (e.g., 'New', 'In Progress', 'Closed')",
    type=str
)
parser.add_argument(
    "--severity",
    help="Filter by severity level (e.g., 'High', 'Medium', 'Low')",
    type=str
)
parser.add_argument(
    "--assignee",
    help="Filter by assignee username",
    type=str
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

def format_date(date_str):
    """Format ISO date string to readable format."""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except (ValueError, TypeError):
        return date_str[:16] if len(date_str) > 16 else date_str

def build_search_query():
    """Build search query from command line arguments."""
    query_parts = []

    if args.query:
        query_parts.append(args.query)

    if args.status:
        query_parts.append(f"status:{args.status}")

    if args.severity:
        query_parts.append(f"severity:{args.severity}")

    if args.assignee:
        query_parts.append(f"assignee:{args.assignee}")

    return " ".join(query_parts) if query_parts else None

def format_table_output(insights):
    """Format insights as a table."""
    if not insights:
        print("No insights found.")
        return

    # Print header
    print(f"{'ID':<20} {'Name':<30} {'Severity':<8} {'Status':<12} {'Created':<16}")
    print("-" * 88)

    for insight in insights:
        # Safely extract fields with defaults
        insight_id = insight.get('id', 'N/A')[:20]
        name = insight.get('name', 'N/A')[:30]
        severity = insight.get('severity', 'N/A')[:8]
        status = insight.get('status', {}).get('displayName', 'N/A')[:12]
        created = format_date(insight.get('created'))

        print(f"{insight_id:<20} {name:<30} {severity:<8} {status:<12} {created:<16}")

def format_details_output(insights):
    """Format insights with detailed information."""
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

        # Entity information
        entity = insight.get('entity')
        if entity:
            entity_name = entity.get('hostname', entity.get('value', 'N/A'))
            entity_type = entity.get('entityType', 'N/A')
            print(f"Entity: {entity_name} ({entity_type})")

        # Signal information
        signals = insight.get('signals', [])
        if signals:
            print(f"Signal Count: {len(signals)}")
            if len(signals) <= 3:
                for signal in signals:
                    signal_name = signal.get('name', 'N/A')
                    signal_stage = signal.get('stage', 'N/A')
                    print(f"  - {signal_name} (Stage: {signal_stage})")
            else:
                print(f"  - First 3 signals of {len(signals)} total:")
                for signal in signals[:3]:
                    signal_name = signal.get('name', 'N/A')
                    signal_stage = signal.get('stage', 'N/A')
                    print(f"    - {signal_name} (Stage: {signal_stage})")

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

def main():
    """Main execution function."""
    try:
        # Build search query from arguments
        search_query = build_search_query()

        if search_query:
            logger.info(f"Querying insights with query: '{search_query}' (limit: {args.limit})")
        else:
            logger.info(f"Querying all insights (limit: {args.limit})")

        # Query insights using pagination
        insights = cse.query_insights(q=search_query, limit=args.limit)

        logger.info(f"Retrieved {len(insights)} insights")

        # Output results based on format
        if args.output_format == "json":
            print(json.dumps(insights, indent=2))
        elif args.output_format == "details":
            format_details_output(insights)
        else:  # table format
            format_table_output(insights)

        # Show summary if we have insights
        if insights and args.output_format != "json":
            # Severity breakdown
            severity_counts = {}
            status_counts = {}

            for insight in insights:
                severity = insight.get('severity', 'Unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

                status = insight.get('status', {}).get('displayName', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1

            print(f"\nSummary: {len(insights)} insights retrieved")

            if severity_counts:
                severity_info = [f"{sev}: {count}" for sev, count in sorted(severity_counts.items())]
                print(f"Severity breakdown: {', '.join(severity_info)}")

            if status_counts:
                status_info = [f"{status}: {count}" for status, count in sorted(status_counts.items())]
                print(f"Status breakdown: {', '.join(status_info)}")

            # Show applied filters
            if search_query:
                print(f"Query used: '{search_query}'")

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

