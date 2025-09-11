#!/usr/bin/env python3
"""
Rule Tuning Expression Details Demo

This script demonstrates how to retrieve detailed information about specific
rule tuning expressions and analyze their configuration.

Features:
- Get specific rule tuning expression by ID
- Analyze rule tuning expression structure
- Show expression syntax and logic
- Display associated rule information
"""

import argparse
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
    description="Get detailed information about rule tuning expressions"
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
    "--expression-id",
    help="Specific rule tuning expression ID to retrieve details for",
    type=str
)
parser.add_argument(
    "--search-term",
    help="Search for expressions containing this term in name or description",
    type=str
)
parser.add_argument(
    "--limit",
    help="Maximum number of expressions to analyze (default: 50)",
    type=int,
    default=50
)
parser.add_argument(
    "--show-expressions",
    help="Show the actual tuning expression syntax",
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
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except (ValueError, TypeError):
        return date_str

def display_expression_details(expression):
    """Display detailed information about a rule tuning expression."""
    print("=" * 80)
    print("Rule Tuning Expression Details")
    print("=" * 80)

    # Basic information
    print(f"ID: {expression.get('id', 'N/A')}")
    print(f"Name: {expression.get('name', 'N/A')}")
    print(f"Enabled: {'Yes' if expression.get('enabled', False) else 'No'}")
    print(f"Created: {format_date(expression.get('createdAt'))}")
    print(f"Modified: {format_date(expression.get('modifiedAt'))}")

    # Rule information
    if 'ruleId' in expression or 'ruleName' in expression:
        print("\nAssociated Rule:")
        print(f"  Rule ID: {expression.get('ruleId', 'N/A')}")
        print(f"  Rule Name: {expression.get('ruleName', 'N/A')}")

    # Description
    if expression.get('description'):
        print("\nDescription:")
        print(f"  {expression['description']}")

    # Expression details
    if args.show_expressions:
        print("\nTuning Expression Details:")
        if 'expression' in expression:
            print(f"  Expression: {expression['expression']}")
        if 'excludedFieldValues' in expression:
            excluded = expression['excludedFieldValues']
            if excluded:
                print("  Excluded Values:")
                for field, values in excluded.items():
                    if isinstance(values, list):
                        print(f"    {field}: {', '.join(map(str, values))}")
                    else:
                        print(f"    {field}: {values}")

    # Additional metadata
    if 'createdBy' in expression or 'modifiedBy' in expression:
        print("\nAudit Information:")
        if 'createdBy' in expression:
            print(f"  Created By: {expression['createdBy']}")
        if 'modifiedBy' in expression:
            print(f"  Modified By: {expression['modifiedBy']}")

    print()

def search_expressions(expressions, search_term):
    """Search for expressions containing the search term."""
    if not search_term:
        return expressions

    search_term = search_term.lower()
    matching_expressions = []

    for expr in expressions:
        # Search in name, description, rule name
        name = expr.get('name', '').lower()
        description = expr.get('description', '').lower()
        rule_name = expr.get('ruleName', '').lower()

        if (search_term in name or
            search_term in description or
            search_term in rule_name):
            matching_expressions.append(expr)

    return matching_expressions

def main():
    """Main execution function."""
    try:
        if args.expression_id:
            # Get specific expression by ID
            logger.info(f"Retrieving rule tuning expression: {args.expression_id}")
            expression_data = cse.get_rule_tuning_expression(args.expression_id)

            # Handle response format
            if isinstance(expression_data, dict) and 'data' in expression_data:
                expression = expression_data['data']
            else:
                expression = expression_data

            display_expression_details(expression)

        else:
            # Get all expressions and optionally search/filter
            logger.info(f"Retrieving rule tuning expressions (limit: {args.limit})")

            expressions_data = cse.get_rule_tuning_expressions(limit=args.limit)

            # Extract expressions from response
            if isinstance(expressions_data, dict) and 'data' in expressions_data:
                if 'objects' in expressions_data['data']:
                    expressions = expressions_data['data']['objects']
                else:
                    expressions = expressions_data['data']
            else:
                expressions = expressions_data if isinstance(expressions_data, list) else []

            logger.info(f"Retrieved {len(expressions)} rule tuning expressions")

            # Apply search filter if provided
            if args.search_term:
                expressions = search_expressions(expressions, args.search_term)
                logger.info(f"Found {len(expressions)} expressions matching '{args.search_term}'")

            if not expressions:
                print("No rule tuning expressions found matching your criteria.")
                return

            # Display results
            if len(expressions) == 1:
                display_expression_details(expressions[0])
            else:
                print(f"\nFound {len(expressions)} rule tuning expressions:")
                print("-" * 120)
                print(f"{'ID':<20} {'Name':<30} {'Rule Name':<25} {'Enabled':<8} {'Created':<12}")
                print("-" * 120)

                for expr in expressions:
                    expr_id = expr.get('id', 'N/A')[:20]
                    name = expr.get('name', 'N/A')[:30]
                    rule_name = expr.get('ruleName', 'N/A')[:25]
                    enabled = 'Yes' if expr.get('enabled', False) else 'No'
                    created = expr.get('createdAt', 'N/A')

                    if created != 'N/A':
                        try:
                            created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                            created = created_dt.strftime('%Y-%m-%d')
                        except (ValueError, TypeError):
                            created = created[:12]

                    print(f"{expr_id:<20} {name:<30} {rule_name:<25} {enabled:<8} {created:<12}")

                print("\nTip: Use --expression-id <ID> to get detailed information about a specific expression")
                print("Tip: Use --show-expressions to see the actual tuning expression syntax")

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

