#!/usr/bin/env python3
"""
Tag Schemas Demo Script

This script demonstrates how to retrieve and work with tag schemas
using the Sumo Logic Cloud SIEM Python SDK.

Tag schemas define the structure and validation rules for tags that can be
applied to various Cloud SIEM objects like rules, entities, and insights.
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
    description="Retrieve and display tag schemas from Cloud SIEM"
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
    help="Maximum number of tag schemas to retrieve (default: 100)",
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
    "--schema-id",
    help="Get details for a specific tag schema ID",
    type=str
)
parser.add_argument(
    "--search-term",
    help="Search for schemas containing this term in key or label",
    type=str
)
parser.add_argument(
    "--filter-required",
    help="Show only required tag schemas",
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

def search_schemas(schemas, search_term):
    """Search for schemas containing the search term."""
    if not search_term:
        return schemas

    search_term = search_term.lower()
    matching_schemas = []

    for schema in schemas:
        key = schema.get('key', '').lower()
        label = schema.get('label', '').lower()

        if search_term in key or search_term in label:
            matching_schemas.append(schema)

    return matching_schemas

def format_table_output(schemas):
    """Format tag schemas as a table."""
    if not schemas:
        print("No tag schemas found.")
        return

    # Print header
    print(f"{'ID':<20} {'Key':<25} {'Label':<25} {'Type':<10} {'Required':<8} {'Created':<12}")
    print("-" * 102)

    for schema in schemas:
        # Safely extract fields with defaults
        schema_id = schema.get('id', 'N/A')[:20]
        key = schema.get('key', 'N/A')[:25]
        label = schema.get('label', 'N/A')[:25]
        content_type = schema.get('contentType', 'N/A')[:10]
        required = 'Yes' if schema.get('required', False) else 'No'
        created = format_date(schema.get('createdAt'))

        print(f"{schema_id:<20} {key:<25} {label:<25} {content_type:<10} {required:<8} {created:<12}")

def format_details_output(schemas):
    """Format tag schemas with detailed information."""
    if not schemas:
        print("No tag schemas found.")
        return

    for i, schema in enumerate(schemas):
        if i > 0:
            print("\n" + "="*80)

        print("Tag Schema Details")
        print("="*80)
        print(f"ID: {schema.get('id', 'N/A')}")
        print(f"Key: {schema.get('key', 'N/A')}")
        print(f"Label: {schema.get('label', 'N/A')}")
        print(f"Content Type: {schema.get('contentType', 'N/A')}")
        print(f"Required: {'Yes' if schema.get('required', False) else 'No'}")

        # Description
        if schema.get('description'):
            print(f"Description: {schema['description']}")

        # Help text
        if schema.get('helpText'):
            print(f"Help Text: {schema['helpText']}")

        # Validation rules
        if schema.get('validationRules'):
            print("Validation Rules:")
            rules = schema['validationRules']
            if isinstance(rules, list):
                for rule in rules:
                    if isinstance(rule, dict):
                        rule_type = rule.get('type', 'N/A')
                        rule_value = rule.get('value', 'N/A')
                        print(f"  - {rule_type}: {rule_value}")
                    else:
                        print(f"  - {rule}")
            else:
                print(f"  {rules}")

        # Default value
        if schema.get('defaultValue'):
            print(f"Default Value: {schema['defaultValue']}")

        # Options/choices (for select types)
        if schema.get('options'):
            options = schema['options']
            if isinstance(options, list):
                print("Available Options:")
                for option in options[:10]:  # Show first 10 options
                    if isinstance(option, dict):
                        opt_label = option.get('label', 'N/A')
                        opt_value = option.get('value', 'N/A')
                        print(f"  - {opt_label} ({opt_value})")
                    else:
                        print(f"  - {option}")
                if len(options) > 10:
                    print(f"  ... and {len(options) - 10} more options")
            else:
                print(f"Options: {options}")

        # Constraints
        if schema.get('minLength') is not None:
            print(f"Minimum Length: {schema['minLength']}")
        if schema.get('maxLength') is not None:
            print(f"Maximum Length: {schema['maxLength']}")
        if schema.get('pattern'):
            print(f"Pattern: {schema['pattern']}")

        # Scope/applicability
        if schema.get('scope'):
            scope = schema['scope']
            if isinstance(scope, list):
                print(f"Applicable To: {', '.join(scope)}")
            else:
                print(f"Applicable To: {scope}")

        # Visibility settings
        if 'visible' in schema:
            visible = 'Yes' if schema['visible'] else 'No'
            print(f"Visible: {visible}")

        if 'editable' in schema:
            editable = 'Yes' if schema['editable'] else 'No'
            print(f"Editable: {editable}")

        # Audit information
        print(f"Created: {format_date(schema.get('createdAt'))}")
        print(f"Modified: {format_date(schema.get('modifiedAt'))}")
        if schema.get('createdBy'):
            print(f"Created By: {schema['createdBy']}")
        if schema.get('modifiedBy'):
            print(f"Modified By: {schema['modifiedBy']}")

def main():
    """Main execution function."""
    try:
        if args.schema_id:
            # Get specific schema by ID
            logger.info(f"Retrieving tag schema: {args.schema_id}")
            schema_data = cse.get_tag_schema(args.schema_id)

            # Handle response format
            if isinstance(schema_data, dict) and 'data' in schema_data:
                schema = schema_data['data']
            else:
                schema = schema_data

            format_details_output([schema])

        else:
            # Get all tag schemas
            logger.info(f"Retrieving tag schemas (limit: {args.limit})")

            schemas_data = cse.get_tag_schemas(limit=args.limit)

            # Extract schemas from response
            if isinstance(schemas_data, dict) and 'data' in schemas_data:
                if 'objects' in schemas_data['data']:
                    schemas = schemas_data['data']['objects']
                else:
                    schemas = schemas_data['data']
            else:
                schemas = schemas_data if isinstance(schemas_data, list) else []

            logger.info(f"Retrieved {len(schemas)} tag schemas")

            # Apply search filter if provided
            if args.search_term:
                schemas = search_schemas(schemas, args.search_term)
                logger.info(f"Found {len(schemas)} schemas matching '{args.search_term}'")

            # Apply required filter if requested
            if args.filter_required:
                schemas = [schema for schema in schemas if schema.get('required', False)]
                logger.info(f"Filtered to {len(schemas)} required schemas")

            # Output results based on format
            if args.output_format == "json":
                print(json.dumps(schemas, indent=2))
            elif args.output_format == "details":
                format_details_output(schemas)
            else:  # table format
                format_table_output(schemas)

            # Show summary if we have schemas
            if schemas and args.output_format != "json":
                total_required = sum(1 for s in schemas if s.get('required', False))

                # Content type breakdown
                content_types = {}
                for schema in schemas:
                    content_type = schema.get('contentType', 'Unknown')
                    content_types[content_type] = content_types.get(content_type, 0) + 1

                print(f"\nSummary: {len(schemas)} tag schemas ({total_required} required)")
                if content_types:
                    type_info = [f"{ctype}: {count}" for ctype, count in content_types.items()]
                    print(f"Content types: {', '.join(type_info)}")

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
