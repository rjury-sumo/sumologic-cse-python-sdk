#!/usr/bin/env python3
"""
Custom Insights Demo Script

This script demonstrates how to retrieve and work with custom insights
using the Sumo Logic Cloud SIEM Python SDK.

Custom insights are user-defined insight types that extend Cloud SIEM's
detection capabilities beyond the built-in insight types.
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
    description="Retrieve and display custom insights from Cloud SIEM"
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
    help="Maximum number of custom insights to retrieve (default: 100)",
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
    "--insight-id",
    help="Get details for a specific custom insight ID",
    type=str
)
parser.add_argument(
    "--filter-enabled",
    help="Show only enabled custom insights",
    action="store_true"
)
parser.add_argument(
    "--search-term",
    help="Search for insights containing this term in name or description",
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

def search_insights(insights, search_term):
    """Search for insights containing the search term."""
    if not search_term:
        return insights
    
    search_term = search_term.lower()
    matching_insights = []
    
    for insight in insights:
        name = insight.get('name', '').lower()
        description = insight.get('description', '').lower()
        
        if search_term in name or search_term in description:
            matching_insights.append(insight)
    
    return matching_insights

def format_table_output(insights):
    """Format custom insights as a table."""
    if not insights:
        print("No custom insights found.")
        return
    
    # Print header
    print(f"{'ID':<20} {'Name':<35} {'Enabled':<8} {'Severity':<8} {'Created':<12}")
    print("-" * 85)
    
    for insight in insights:
        # Safely extract fields with defaults
        insight_id = insight.get('id', 'N/A')[:20]
        name = insight.get('name', 'N/A')[:35]
        enabled = 'Yes' if insight.get('enabled', False) else 'No'
        severity = str(insight.get('severity', 'N/A'))[:8]
        created = format_date(insight.get('createdAt'))
        
        print(f"{insight_id:<20} {name:<35} {enabled:<8} {severity:<8} {created:<12}")

def format_details_output(insights):
    """Format custom insights with detailed information."""
    if not insights:
        print("No custom insights found.")
        return
    
    for i, insight in enumerate(insights):
        if i > 0:
            print("\n" + "="*80)
        
        print(f"Custom Insight Details")
        print("="*80)
        print(f"ID: {insight.get('id', 'N/A')}")
        print(f"Name: {insight.get('name', 'N/A')}")
        print(f"Enabled: {'Yes' if insight.get('enabled', False) else 'No'}")
        print(f"Severity: {insight.get('severity', 'N/A')}")
        
        if insight.get('description'):
            print(f"Description: {insight['description']}")
        
        # Signal rules and conditions
        if insight.get('signalNames'):
            signal_names = insight['signalNames']
            if isinstance(signal_names, list):
                print(f"Signal Names: {', '.join(signal_names)}")
            else:
                print(f"Signal Names: {signal_names}")
        
        # Ordered field information
        if insight.get('orderedFields'):
            print("Ordered Fields:")
            for field in insight['orderedFields']:
                print(f"  - {field}")
        
        # Resolution information
        if insight.get('resolution'):
            resolution = insight['resolution']
            if isinstance(resolution, dict):
                res_name = resolution.get('name', 'N/A')
                print(f"Default Resolution: {res_name}")
            else:
                print(f"Default Resolution: {resolution}")
        
        # Status information
        if insight.get('status'):
            status = insight['status']
            if isinstance(status, dict):
                status_name = status.get('name', 'N/A')
                print(f"Default Status: {status_name}")
            else:
                print(f"Default Status: {status}")
        
        # Tags
        if insight.get('tags'):
            tags = insight['tags']
            if isinstance(tags, list):
                print(f"Tags: {', '.join(tags)}")
            else:
                print(f"Tags: {tags}")
        
        # Audit information
        print(f"Created: {format_date(insight.get('createdAt'))}")
        print(f"Modified: {format_date(insight.get('modifiedAt'))}")
        if insight.get('createdBy'):
            print(f"Created By: {insight['createdBy']}")
        if insight.get('modifiedBy'):
            print(f"Modified By: {insight['modifiedBy']}")

def main():
    """Main execution function."""
    try:
        if args.insight_id:
            # Get specific insight by ID
            logger.info(f"Retrieving custom insight: {args.insight_id}")
            insight_data = cse.get_custom_insight(args.insight_id)
            
            # Handle response format
            if isinstance(insight_data, dict) and 'data' in insight_data:
                insight = insight_data['data']
            else:
                insight = insight_data
            
            format_details_output([insight])
            
        else:
            # Get all custom insights
            logger.info(f"Retrieving custom insights (limit: {args.limit})")
            
            insights_data = cse.get_custom_insights(limit=args.limit)
            
            # Extract insights from response
            if isinstance(insights_data, dict) and 'data' in insights_data:
                if 'objects' in insights_data['data']:
                    insights = insights_data['data']['objects']
                else:
                    insights = insights_data['data']
            else:
                insights = insights_data if isinstance(insights_data, list) else []
            
            logger.info(f"Retrieved {len(insights)} custom insights")
            
            # Apply search filter if provided
            if args.search_term:
                insights = search_insights(insights, args.search_term)
                logger.info(f"Found {len(insights)} insights matching '{args.search_term}'")
            
            # Apply filtering if requested
            if args.filter_enabled:
                insights = [insight for insight in insights if insight.get('enabled', False)]
                logger.info(f"Filtered to {len(insights)} enabled insights")
            
            # Output results based on format
            if args.output_format == "json":
                print(json.dumps(insights, indent=2))
            elif args.output_format == "details":
                format_details_output(insights)
            else:  # table format
                format_table_output(insights)
            
            # Show summary if we have insights
            if insights and args.output_format != "json":
                total_enabled = sum(1 for i in insights if i.get('enabled', False))
                
                # Severity breakdown
                severity_counts = {}
                for insight in insights:
                    severity = insight.get('severity', 'Unknown')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                print(f"\nSummary: {len(insights)} custom insights ({total_enabled} enabled)")
                if severity_counts:
                    severity_info = [f"{sev}: {count}" for sev, count in severity_counts.items()]
                    print(f"Severity breakdown: {', '.join(severity_info)}")
        
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