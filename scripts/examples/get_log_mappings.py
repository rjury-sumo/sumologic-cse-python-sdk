#!/usr/bin/env python3
"""
Log Mappings Demo Script

This script demonstrates how to retrieve and work with log mappings
using the Sumo Logic Cloud SIEM Python SDK.

Log mappings define how raw log data is parsed and normalized into
Cloud SIEM's common information model for analysis and correlation.
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
    description="Retrieve and display log mappings from Cloud SIEM"
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
    help="Maximum number of log mappings to retrieve (default: 100)",
    type=int,
    default=100
)
parser.add_argument(
    "--output-format",
    help="Output format: table, json, details, or vendors (default: table)",
    choices=["table", "json", "details", "vendors"],
    default="table"
)
parser.add_argument(
    "--mapping-id",
    help="Get details for a specific log mapping ID",
    type=str
)
parser.add_argument(
    "--filter-enabled",
    help="Show only enabled log mappings",
    action="store_true"
)
parser.add_argument(
    "--search-term",
    help="Search for mappings containing this term in name, vendor, or product",
    type=str
)
parser.add_argument(
    "--vendor",
    help="Filter by vendor name",
    type=str
)
parser.add_argument(
    "--product",
    help="Filter by product name",
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

def search_mappings(mappings, search_term):
    """Search for mappings containing the search term."""
    if not search_term:
        return mappings

    search_term = search_term.lower()
    matching_mappings = []

    for mapping in mappings:
        name = mapping.get('name', '').lower()
        vendor = mapping.get('vendor', '').lower()
        product = mapping.get('product', '').lower()

        if (search_term in name or
            search_term in vendor or
            search_term in product):
            matching_mappings.append(mapping)

    return matching_mappings

def filter_by_vendor_product(mappings, vendor, product):
    """Filter mappings by vendor and/or product."""
    filtered_mappings = mappings

    if vendor:
        vendor_lower = vendor.lower()
        filtered_mappings = [m for m in filtered_mappings
                           if vendor_lower in m.get('vendor', '').lower()]

    if product:
        product_lower = product.lower()
        filtered_mappings = [m for m in filtered_mappings
                           if product_lower in m.get('product', '').lower()]

    return filtered_mappings

def format_table_output(mappings):
    """Format log mappings as a table."""
    if not mappings:
        print("No log mappings found.")
        return

    # Print header
    print(f"{'ID':<20} {'Name':<25} {'Vendor':<15} {'Product':<15} {'Enabled':<8} {'Created':<12}")
    print("-" * 102)

    for mapping in mappings:
        # Safely extract fields with defaults
        mapping_id = mapping.get('id', 'N/A')[:20]
        name = mapping.get('name', 'N/A')[:25]
        vendor = mapping.get('vendor', 'N/A')[:15]
        product = mapping.get('product', 'N/A')[:15]
        enabled = 'Yes' if mapping.get('enabled', False) else 'No'
        created = format_date(mapping.get('createdAt'))

        print(f"{mapping_id:<20} {name:<25} {vendor:<15} {product:<15} {enabled:<8} {created:<12}")

def format_details_output(mappings):
    """Format log mappings with detailed information."""
    if not mappings:
        print("No log mappings found.")
        return

    for i, mapping in enumerate(mappings):
        if i > 0:
            print("\n" + "="*80)

        print("Log Mapping Details")
        print("="*80)
        print(f"ID: {mapping.get('id', 'N/A')}")
        print(f"Name: {mapping.get('name', 'N/A')}")
        print(f"Enabled: {'Yes' if mapping.get('enabled', False) else 'No'}")
        print(f"Vendor: {mapping.get('vendor', 'N/A')}")
        print(f"Product: {mapping.get('product', 'N/A')}")

        # Version information
        if mapping.get('version'):
            print(f"Version: {mapping['version']}")

        # Event ID mapping
        if mapping.get('eventIdPattern'):
            print(f"Event ID Pattern: {mapping['eventIdPattern']}")

        # Log format
        if mapping.get('logFormat'):
            print(f"Log Format: {mapping['logFormat']}")

        # Parser information
        if mapping.get('parserName'):
            print(f"Parser Name: {mapping['parserName']}")

        # Field mappings
        if mapping.get('fieldMappings'):
            print("Field Mappings:")
            field_mappings = mapping['fieldMappings']
            if isinstance(field_mappings, list):
                for field_map in field_mappings[:5]:  # Show first 5 mappings
                    if isinstance(field_map, dict):
                        source = field_map.get('sourceField', 'N/A')
                        target = field_map.get('targetField', 'N/A')
                        print(f"  - {source} -> {target}")
                    else:
                        print(f"  - {field_map}")
                if len(field_mappings) > 5:
                    print(f"  ... and {len(field_mappings) - 5} more mappings")
            else:
                print(f"  {field_mappings}")

        # Structured fields
        if mapping.get('structuredFields'):
            structured = mapping['structuredFields']
            if isinstance(structured, list):
                print(f"Structured Fields: {', '.join(structured[:10])}")
                if len(structured) > 10:
                    print(f"  ... and {len(structured) - 10} more fields")
            else:
                print(f"Structured Fields: {structured}")

        # Sample log
        if mapping.get('sampleLog'):
            sample_log = mapping['sampleLog']
            # Truncate long sample logs
            if len(sample_log) > 200:
                sample_log = sample_log[:200] + "..."
            print(f"Sample Log: {sample_log}")

        # Audit information
        print(f"Created: {format_date(mapping.get('createdAt'))}")
        print(f"Modified: {format_date(mapping.get('modifiedAt'))}")
        if mapping.get('createdBy'):
            print(f"Created By: {mapping['createdBy']}")
        if mapping.get('modifiedBy'):
            print(f"Modified By: {mapping['modifiedBy']}")

def format_vendors_output():
    """Format vendors and products information."""
    try:
        vendors_data = cse.get_log_mapping_vendors_and_products()

        # Handle response format
        if isinstance(vendors_data, dict) and 'data' in vendors_data:
            vendors_info = vendors_data['data']
        else:
            vendors_info = vendors_data

        print("Available Log Mapping Vendors and Products")
        print("="*50)

        if isinstance(vendors_info, dict):
            for vendor_name, products in vendors_info.items():
                print(f"\n{vendor_name}:")
                if isinstance(products, list):
                    for product in products:
                        print(f"  - {product}")
                else:
                    print(f"  - {products}")
        else:
            print(json.dumps(vendors_info, indent=2))

    except Exception as e:
        logger.error(f"Failed to retrieve vendors and products: {e}")

def main():
    """Main execution function."""
    try:
        if args.output_format == "vendors":
            # Show vendors and products
            format_vendors_output()
            return

        if args.mapping_id:
            # Get specific mapping by ID
            logger.info(f"Retrieving log mapping: {args.mapping_id}")
            mapping_data = cse.get_log_mapping(args.mapping_id)

            # Handle response format
            if isinstance(mapping_data, dict) and 'data' in mapping_data:
                mapping = mapping_data['data']
            else:
                mapping = mapping_data

            format_details_output([mapping])

        else:
            # Get all log mappings
            logger.info(f"Retrieving log mappings (limit: {args.limit})")

            mappings_data = cse.get_log_mappings(limit=args.limit)

            # Extract mappings from response
            if isinstance(mappings_data, dict) and 'data' in mappings_data:
                if 'objects' in mappings_data['data']:
                    mappings = mappings_data['data']['objects']
                else:
                    mappings = mappings_data['data']
            else:
                mappings = mappings_data if isinstance(mappings_data, list) else []

            logger.info(f"Retrieved {len(mappings)} log mappings")

            # Apply search filter if provided
            if args.search_term:
                mappings = search_mappings(mappings, args.search_term)
                logger.info(f"Found {len(mappings)} mappings matching '{args.search_term}'")

            # Apply vendor/product filters
            if args.vendor or args.product:
                mappings = filter_by_vendor_product(mappings, args.vendor, args.product)
                filter_desc = []
                if args.vendor:
                    filter_desc.append(f"vendor: {args.vendor}")
                if args.product:
                    filter_desc.append(f"product: {args.product}")
                logger.info(f"Filtered to {len(mappings)} mappings by {', '.join(filter_desc)}")

            # Apply enabled filter if requested
            if args.filter_enabled:
                mappings = [mapping for mapping in mappings if mapping.get('enabled', False)]
                logger.info(f"Filtered to {len(mappings)} enabled mappings")

            # Output results based on format
            if args.output_format == "json":
                print(json.dumps(mappings, indent=2))
            elif args.output_format == "details":
                format_details_output(mappings)
            else:  # table format
                format_table_output(mappings)

            # Show summary if we have mappings
            if mappings and args.output_format != "json":
                total_enabled = sum(1 for m in mappings if m.get('enabled', False))

                # Vendor breakdown
                vendors = {}
                for mapping in mappings:
                    vendor = mapping.get('vendor', 'Unknown')
                    vendors[vendor] = vendors.get(vendor, 0) + 1

                print(f"\nSummary: {len(mappings)} log mappings ({total_enabled} enabled)")
                if vendors:
                    vendor_info = [f"{vendor}: {count}" for vendor, count in sorted(vendors.items())]
                    print(f"Top vendors: {', '.join(vendor_info[:5])}")
                    if len(vendors) > 5:
                        print(f"... and {len(vendors) - 5} more vendors")

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
