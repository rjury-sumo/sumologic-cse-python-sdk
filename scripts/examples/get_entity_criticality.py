#!/usr/bin/env python3
"""
Custom Entity Criticality Demo Script

This script demonstrates how to retrieve and work with custom entity criticality configurations
using the Sumo Logic Cloud SIEM Python SDK.

Entity criticality configurations allow you to define the business importance of different
entities, which affects prioritization and scoring in Cloud SIEM insights.
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
    description="Retrieve and display custom entity criticality configurations from Cloud SIEM"
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
    help="Maximum number of criticality configs to retrieve (default: 100)",
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
    "--config-id",
    help="Get details for a specific criticality configuration ID",
    type=str
)
parser.add_argument(
    "--filter-enabled",
    help="Show only enabled criticality configurations",
    action="store_true"
)
parser.add_argument(
    "--search-term",
    help="Search for configs containing this term in name",
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

def search_configs(configs, search_term):
    """Search for configs containing the search term."""
    if not search_term:
        return configs

    search_term = search_term.lower()
    matching_configs = []

    for config in configs:
        name = config.get('name', '').lower()

        if search_term in name:
            matching_configs.append(config)

    return matching_configs

def format_table_output(configs):
    """Format criticality configs as a table."""
    if not configs:
        print("No entity criticality configurations found.")
        return

    # Print header
    print(f"{'ID':<20} {'Name':<30} {'Criticality':<12} {'Enabled':<8} {'Created':<12}")
    print("-" * 84)

    for config in configs:
        # Safely extract fields with defaults
        config_id = config.get('id', 'N/A')[:20]
        name = config.get('name', 'N/A')[:30]
        criticality = str(config.get('criticality', 'N/A'))[:12]
        enabled = 'Yes' if config.get('enabled', False) else 'No'
        created = format_date(config.get('createdAt'))

        print(f"{config_id:<20} {name:<30} {criticality:<12} {enabled:<8} {created:<12}")

def format_details_output(configs):
    """Format criticality configs with detailed information."""
    if not configs:
        print("No entity criticality configurations found.")
        return

    for i, config in enumerate(configs):
        if i > 0:
            print("\n" + "="*80)

        print("Entity Criticality Configuration Details")
        print("="*80)
        print(f"ID: {config.get('id', 'N/A')}")
        print(f"Name: {config.get('name', 'N/A')}")
        print(f"Enabled: {'Yes' if config.get('enabled', False) else 'No'}")
        print(f"Criticality Level: {config.get('criticality', 'N/A')}")

        # Expression/criteria for matching entities
        if config.get('expression'):
            print(f"Matching Expression: {config['expression']}")

        # Entity type
        if config.get('entityType'):
            print(f"Entity Type: {config['entityType']}")

        # Field mappings and criteria
        if config.get('fieldMappings'):
            print("Field Mappings:")
            for mapping in config['fieldMappings']:
                field_name = mapping.get('fieldName', 'N/A')
                field_value = mapping.get('fieldValue', 'N/A')
                print(f"  - {field_name}: {field_value}")

        # Tags
        if config.get('tags'):
            tags = config['tags']
            if isinstance(tags, list):
                print(f"Tags: {', '.join(str(tag) for tag in tags)}")
            else:
                print(f"Tags: {tags}")

        # Priority/weight
        if config.get('weight') is not None:
            print(f"Weight: {config['weight']}")

        # Description or notes
        if config.get('description'):
            print(f"Description: {config['description']}")

        # Scope information
        if config.get('scope'):
            scope = config['scope']
            print(f"Scope: {scope}")

        # Network information (if applicable)
        if config.get('network'):
            network = config['network']
            if isinstance(network, dict):
                hostname = network.get('hostname', 'N/A')
                cidr = network.get('cidr', 'N/A')
                print(f"Network: {hostname} ({cidr})")
            else:
                print(f"Network: {network}")

        # Audit information
        print(f"Created: {format_date(config.get('createdAt'))}")
        print(f"Modified: {format_date(config.get('modifiedAt'))}")
        if config.get('createdBy'):
            print(f"Created By: {config['createdBy']}")
        if config.get('modifiedBy'):
            print(f"Modified By: {config['modifiedBy']}")

def main():
    """Main execution function."""
    try:
        if args.config_id:
            # Get specific config by ID
            logger.info(f"Retrieving entity criticality config: {args.config_id}")
            config_data = cse.get_entity_criticality_config(args.config_id)

            # Handle response format
            if isinstance(config_data, dict) and 'data' in config_data:
                config = config_data['data']
            else:
                config = config_data

            format_details_output([config])

        else:
            # Get all criticality configs
            logger.info(f"Retrieving entity criticality configurations (limit: {args.limit})")

            configs_data = cse.get_entity_criticality_configs(limit=args.limit)

            # Extract configs from response
            if isinstance(configs_data, dict) and 'data' in configs_data:
                if 'objects' in configs_data['data']:
                    configs = configs_data['data']['objects']
                else:
                    configs = configs_data['data']
            else:
                configs = configs_data if isinstance(configs_data, list) else []

            logger.info(f"Retrieved {len(configs)} entity criticality configurations")

            # Apply search filter if provided
            if args.search_term:
                configs = search_configs(configs, args.search_term)
                logger.info(f"Found {len(configs)} configs matching '{args.search_term}'")

            # Apply filtering if requested
            if args.filter_enabled:
                configs = [config for config in configs if config.get('enabled', False)]
                logger.info(f"Filtered to {len(configs)} enabled configurations")

            # Output results based on format
            if args.output_format == "json":
                print(json.dumps(configs, indent=2))
            elif args.output_format == "details":
                format_details_output(configs)
            else:  # table format
                format_table_output(configs)

            # Show summary if we have configs
            if configs and args.output_format != "json":
                total_enabled = sum(1 for c in configs if c.get('enabled', False))

                # Criticality level breakdown
                criticality_levels = {}
                for config in configs:
                    level = config.get('criticality', 'Unknown')
                    criticality_levels[level] = criticality_levels.get(level, 0) + 1

                print(f"\nSummary: {len(configs)} criticality configurations ({total_enabled} enabled)")
                if criticality_levels:
                    level_info = [f"{level}: {count}" for level, count in criticality_levels.items()]
                    print(f"Criticality levels: {', '.join(level_info)}")

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
