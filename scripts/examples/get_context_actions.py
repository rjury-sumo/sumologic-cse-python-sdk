#!/usr/bin/env python3
"""
Context Actions Demo Script

This script demonstrates how to retrieve and work with context actions
using the Sumo Logic Cloud SIEM Python SDK.

Context actions are configurable actions that can be performed from the Cloud SIEM UI,
such as enrichment lookups, external tool integrations, and automated responses.
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
    description="Retrieve and display context actions from Cloud SIEM"
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
    help="Maximum number of context actions to retrieve (default: 100)",
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
    "--action-id",
    help="Get details for a specific context action ID",
    type=str
)
parser.add_argument(
    "--filter-enabled",
    help="Show only enabled context actions",
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

def format_date(date_str):
    """Format ISO date string to readable format."""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return date_str[:10] if len(date_str) > 10 else date_str

def format_table_output(actions):
    """Format context actions as a table."""
    if not actions:
        print("No context actions found.")
        return

    # Print header
    print(f"{'ID':<20} {'Name':<30} {'Type':<15} {'Enabled':<8} {'Created':<12}")
    print("-" * 87)

    for action in actions:
        # Safely extract fields with defaults
        action_id = action.get('id', 'N/A')[:20]
        name = action.get('name', 'N/A')[:30]
        action_type = action.get('type', 'N/A')[:15]
        enabled = 'Yes' if action.get('enabled', False) else 'No'
        created = format_date(action.get('createdAt'))

        print(f"{action_id:<20} {name:<30} {action_type:<15} {enabled:<8} {created:<12}")

def format_details_output(actions):
    """Format context actions with detailed information."""
    if not actions:
        print("No context actions found.")
        return

    for i, action in enumerate(actions):
        if i > 0:
            print("\n" + "="*80)

        print("Context Action Details")
        print("="*80)
        print(f"ID: {action.get('id', 'N/A')}")
        print(f"Name: {action.get('name', 'N/A')}")
        print(f"Type: {action.get('type', 'N/A')}")
        print(f"Enabled: {'Yes' if action.get('enabled', False) else 'No'}")

        if action.get('description'):
            print(f"Description: {action['description']}")

        # URL and template information
        if action.get('template'):
            template = action['template']
            if template.get('url'):
                print(f"URL Template: {template['url']}")
            if template.get('method'):
                print(f"HTTP Method: {template['method']}")

        # Parameters
        if action.get('parameters'):
            print("Parameters:")
            for param in action['parameters']:
                param_name = param.get('name', 'N/A')
                param_type = param.get('type', 'N/A')
                required = 'Required' if param.get('required', False) else 'Optional'
                print(f"  - {param_name} ({param_type}) - {required}")

        # Audit information
        print(f"Created: {format_date(action.get('createdAt'))}")
        print(f"Modified: {format_date(action.get('modifiedAt'))}")
        if action.get('createdBy'):
            print(f"Created By: {action['createdBy']}")
        if action.get('modifiedBy'):
            print(f"Modified By: {action['modifiedBy']}")

def main():
    """Main execution function."""
    try:
        if args.action_id:
            # Get specific action by ID
            logger.info(f"Retrieving context action: {args.action_id}")
            action_data = cse.get_context_action(args.action_id)

            # Handle response format
            if isinstance(action_data, dict) and 'data' in action_data:
                action = action_data['data']
            else:
                action = action_data

            format_details_output([action])

        else:
            # Get all context actions
            logger.info(f"Retrieving context actions (limit: {args.limit})")

            actions_data = cse.get_context_actions(limit=args.limit)

            # Extract actions from response
            if isinstance(actions_data, dict) and 'data' in actions_data:
                if 'objects' in actions_data['data']:
                    actions = actions_data['data']['objects']
                else:
                    actions = actions_data['data']
            else:
                actions = actions_data if isinstance(actions_data, list) else []

            logger.info(f"Retrieved {len(actions)} context actions")

            # Apply filtering if requested
            if args.filter_enabled:
                actions = [action for action in actions if action.get('enabled', False)]
                logger.info(f"Filtered to {len(actions)} enabled actions")

            # Output results based on format
            if args.output_format == "json":
                print(json.dumps(actions, indent=2))
            elif args.output_format == "details":
                format_details_output(actions)
            else:  # table format
                format_table_output(actions)

            # Show summary if we have actions
            if actions and args.output_format != "json":
                total_enabled = sum(1 for a in actions if a.get('enabled', False))
                print(f"\nSummary: {len(actions)} context actions ({total_enabled} enabled)")

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
