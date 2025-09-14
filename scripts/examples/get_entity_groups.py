#!/usr/bin/env python3
"""
Entity Group Configurations Demo Script

This script demonstrates how to retrieve and work with entity group configurations
using the Sumo Logic Cloud SIEM Python SDK.

Entity groups allow you to organize and categorize entities for better visibility
and management within Cloud SIEM, such as grouping servers by environment or
users by department.
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
    description="Retrieve and display entity group configurations from Cloud SIEM"
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
    help="Maximum number of entity groups to retrieve (default: 100)",
    type=int,
    default=100
)
parser.add_argument(
    "--output-format",
    help="Output format: table, json, or details (default: table)",
    choices=["table", "json", "details"],
    default="table"
)
parser.add_argument(
    "--group-id",
    help="Get details for a specific entity group ID",
    type=str
)
parser.add_argument(
    "--filter-enabled",
    help="Show only enabled entity groups",
    action="store_true"
)
parser.add_argument(
    "--search-term",
    help="Search for groups containing this term in name or description",
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
        return dt.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return date_str[:10] if len(date_str) > 10 else date_str

def search_groups(groups, search_term):
    """Search for groups containing the search term."""
    if not search_term:
        return groups

    search_term = search_term.lower()
    matching_groups = []

    for group in groups:
        name = group.get('name', '').lower()
        description = group.get('description', '').lower()

        if search_term in name or search_term in description:
            matching_groups.append(group)

    return matching_groups

def format_table_output(groups):
    """Format entity groups as a table."""
    if not groups:
        print("No entity groups found.")
        return

    # Print header
    print(f"{'ID':<20} {'Name':<30} {'Entity Type':<15} {'Enabled':<8} {'Created':<12}")
    print("-" * 87)

    for group in groups:
        # Safely extract fields with defaults
        group_id = group.get('id', 'N/A')[:20]
        name = group.get('name', 'N/A')[:30]
        entity_type = group.get('entityType', 'N/A')[:15]
        enabled = 'Yes' if group.get('enabled', False) else 'No'
        created = format_date(group.get('createdAt'))

        print(f"{group_id:<20} {name:<30} {entity_type:<15} {enabled:<8} {created:<12}")

def format_details_output(groups):
    """Format entity groups with detailed information."""
    if not groups:
        print("No entity groups found.")
        return

    for i, group in enumerate(groups):
        if i > 0:
            print("\n" + "="*80)

        print("Entity Group Configuration Details")
        print("="*80)
        print(f"ID: {group.get('id', 'N/A')}")
        print(f"Name: {group.get('name', 'N/A')}")
        print(f"Enabled: {'Yes' if group.get('enabled', False) else 'No'}")
        print(f"Entity Type: {group.get('entityType', 'N/A')}")

        if group.get('description'):
            print(f"Description: {group['description']}")

        # Network block information
        if group.get('networkBlock'):
            network_block = group['networkBlock']
            if isinstance(network_block, dict):
                hostname = network_block.get('hostname', 'N/A')
                cidr = network_block.get('cidr', 'N/A')
                print(f"Network Block: {hostname} ({cidr})")
            else:
                print(f"Network Block: {network_block}")

        # Criticality information
        if group.get('criticality'):
            print(f"Criticality: {group['criticality']}")

        # Suppressed information
        if 'suppressed' in group:
            suppressed = 'Yes' if group['suppressed'] else 'No'
            print(f"Suppressed: {suppressed}")

        # Tags
        if group.get('tags'):
            tags = group['tags']
            if isinstance(tags, list):
                print(f"Tags: {', '.join(str(tag) for tag in tags)}")
            else:
                print(f"Tags: {tags}")

        # Expression/criteria
        if group.get('expression'):
            print(f"Expression: {group['expression']}")

        # Entity count (if available)
        if group.get('entityCount') is not None:
            print(f"Entity Count: {group['entityCount']}")

        # Audit information
        print(f"Created: {format_date(group.get('createdAt'))}")
        print(f"Modified: {format_date(group.get('modifiedAt'))}")
        if group.get('createdBy'):
            print(f"Created By: {group['createdBy']}")
        if group.get('modifiedBy'):
            print(f"Modified By: {group['modifiedBy']}")

def main():
    """Main execution function."""
    try:
        if args.group_id:
            # Get specific group by ID
            logger.info(f"Retrieving entity group: {args.group_id}")
            group_data = cse.get_entity_group(args.group_id)

            # Handle response format
            if isinstance(group_data, dict) and 'data' in group_data:
                group = group_data['data']
            else:
                group = group_data

            format_details_output([group])

        else:
            # Get all entity groups
            logger.info(f"Retrieving entity groups (limit: {args.limit})")

            groups_data = cse.get_entity_groups(limit=args.limit)

            # Extract groups from response
            if isinstance(groups_data, dict) and 'data' in groups_data:
                if 'objects' in groups_data['data']:
                    groups = groups_data['data']['objects']
                else:
                    groups = groups_data['data']
            else:
                groups = groups_data if isinstance(groups_data, list) else []

            logger.info(f"Retrieved {len(groups)} entity groups")

            # Apply search filter if provided
            if args.search_term:
                groups = search_groups(groups, args.search_term)
                logger.info(f"Found {len(groups)} groups matching '{args.search_term}'")

            # Apply filtering if requested
            if args.filter_enabled:
                groups = [group for group in groups if group.get('enabled', False)]
                logger.info(f"Filtered to {len(groups)} enabled groups")

            # Output results based on format
            if args.output_format == "json":
                print(json.dumps(groups, indent=2))
            elif args.output_format == "details":
                format_details_output(groups)
            else:  # table format
                format_table_output(groups)

            # Show summary if we have groups
            if groups and args.output_format != "json":
                total_enabled = sum(1 for g in groups if g.get('enabled', False))

                # Entity type breakdown
                entity_types = {}
                for group in groups:
                    entity_type = group.get('entityType', 'Unknown')
                    entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

                print(f"\nSummary: {len(groups)} entity groups ({total_enabled} enabled)")
                if entity_types:
                    type_info = [f"{etype}: {count}" for etype, count in entity_types.items()]
                    print(f"Entity types: {', '.join(type_info)}")

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
