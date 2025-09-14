# Cloud SIEM Python SDK - Example Scripts

This directory contains comprehensive example scripts demonstrating how to use the Sumo Logic Cloud SIEM Python SDK with various API endpoints. These scripts showcase the capabilities introduced in v0.2.0+ and provide practical examples for common Cloud SIEM operations.

## Available Scripts

### Insights Management

#### `query_insights.py`
**Purpose**: Query and search insights with flexible filtering and pagination

**Features**:
- Advanced query capabilities with status, severity, and assignee filtering
- Pagination support for large result sets
- Multiple output formats (table, JSON, details)
- Comprehensive insight details including signals, entities, and audit information

**Usage**:
```bash
# Query high-severity insights
python query_insights.py --severity High --limit 50

# Find insights assigned to specific user
python query_insights.py --assignee "john.doe" --status "In Progress"

# Search with custom query
python query_insights.py --query "malware" --output-format details
```

#### `get_insights_list.py`
**Purpose**: Retrieve insights using offset/limit pagination with summary capabilities

**Features**:
- Simple offset/limit pagination
- Summary view with breakdowns by severity, status, and assignee
- Option to include/exclude closed insights
- Signal information display

**Usage**:
```bash
# Get first 20 insights
python get_insights_list.py

# Get insights with pagination
python get_insights_list.py --offset 50 --limit 25

# Show summary with statistics
python get_insights_list.py --output-format summary --limit 100

# Include closed insights and show signals
python get_insights_list.py --show-closed --show-signals
```

### Detection Rules Management

#### `get_rules.py`
**Purpose**: Retrieve and analyze detection rules with comprehensive filtering

**Features**:
- Get all rules or specific rule by ID
- Filter by enabled status, severity, category
- Search functionality across rule content
- Detailed rule information including MITRE ATT&CK tags
- Summary statistics by rule type and severity

**Usage**:
```bash
# Get all user-created rules (recommended example)
python get_rules.py --query='ruleSource:"user"' --limit 100

# Get specific rule details
python get_rules.py --rule-id "12345-abcde-67890"

# Show only enabled high-severity rules
python get_rules.py --filter-enabled --severity High

# Search for authentication-related rules
python get_rules.py --query "authentication" --output-format details

# Get summary of all rules
python get_rules.py --output-format summary --limit 500
```

### Rule Tuning Management

#### `get_rule_tuning_expressions.py`
**Purpose**: Manage rule tuning expressions to reduce false positives

**Features**:
- List all rule tuning expressions
- Filter by enabled/disabled status
- Multiple output formats with summary statistics
- Pagination support

**Usage**:
```bash
# List all tuning expressions
python get_rule_tuning_expressions.py

# Show only enabled expressions
python get_rule_tuning_expressions.py --filter-enabled

# Get summary statistics
python get_rule_tuning_expressions.py --output-format summary
```

#### `rule_tuning_details.py`
**Purpose**: Get detailed information about specific rule tuning expressions

**Features**:
- Detailed view of specific expressions by ID
- Search by name, description, or rule name
- Display expression syntax and logic
- Associated rule information and audit trail

**Usage**:
```bash
# Get details for specific expression
python rule_tuning_details.py --expression-id "12345-abcde-67890"

# Search for expressions
python rule_tuning_details.py --search-term "failed login" --show-expressions
```

### Entity Management

#### `get_entity_groups.py`
**Purpose**: Manage entity group configurations for organizing entities

**Features**:
- List all entity groups with filtering
- Search by name or description
- Display network blocks, criticality, and entity counts
- Entity type breakdown

**Usage**:
```bash
# List all entity groups
python get_entity_groups.py

# Show only enabled groups
python get_entity_groups.py --filter-enabled

# Search for specific groups
python get_entity_groups.py --search-term "production"
```

#### `get_entity_criticality.py`
**Purpose**: Manage custom entity criticality configurations

**Features**:
- View criticality configurations with field mappings
- Filter by enabled status
- Search functionality
- Criticality level breakdowns

**Usage**:
```bash
# List all criticality configs
python get_entity_criticality.py

# Show detailed configuration information
python get_entity_criticality.py --output-format details
```

### Configuration Management

#### `get_log_mappings.py`
**Purpose**: Manage log parsing and normalization mappings

**Features**:
- List all log mappings with vendor/product filtering
- Display field mappings and sample logs
- Show available vendors and products
- Filter by enabled status

**Usage**:
```bash
# List all log mappings
python get_log_mappings.py

# Show vendors and products
python get_log_mappings.py --output-format vendors

# Filter by vendor
python get_log_mappings.py --vendor Microsoft --product "Windows"

# Show detailed mapping information
python get_log_mappings.py --output-format details --limit 10
```

#### `get_tag_schemas.py`
**Purpose**: Manage tag schema definitions and validation rules

**Features**:
- List all tag schemas with content type breakdown
- Search by key or label
- Display validation rules and constraints
- Show available options for select-type tags

**Usage**:
```bash
# List all tag schemas
python get_tag_schemas.py

# Show only required schemas
python get_tag_schemas.py --filter-required

# Search for specific schemas
python get_tag_schemas.py --search-term "severity"

# Get detailed schema information
python get_tag_schemas.py --output-format details
```

#### `get_context_actions.py`
**Purpose**: Manage context actions for UI integrations

**Features**:
- List all context actions
- Filter by enabled status
- Display URL templates and parameters
- Action type categorization

**Usage**:
```bash
# List all context actions
python get_context_actions.py

# Show detailed action information
python get_context_actions.py --output-format details

# Show only enabled actions
python get_context_actions.py --filter-enabled
```

#### `get_custom_insights.py`
**Purpose**: Manage custom insight definitions

**Features**:
- List custom insight configurations
- Search by name and description
- Display severity breakdown
- Filter by enabled status

**Usage**:
```bash
# List all custom insights
python get_custom_insights.py

# Search for specific insights
python get_custom_insights.py --search-term "suspicious"
```

## Prerequisites

### Authentication

All scripts require Sumo Logic Cloud SIEM API credentials. You can provide these in two ways:

1. **Environment Variables** (Recommended):
   ```bash
   export SUMO_ACCESS_ID="your_access_id_here"
   export SUMO_ACCESS_KEY="your_access_key_here"
   ```

2. **Command Line Arguments**:
   ```bash
   python script_name.py --accessid YOUR_ACCESS_ID --accesskey YOUR_ACCESS_KEY
   ```

### Dependencies

Ensure you have the SDK installed:

```bash
# If running from source
uv run python script_name.py

# If installed as package
pip install sumologiccse
python script_name.py
```

## Common Parameters

All example scripts support these common parameters:

- `--endpoint`: Sumo Logic endpoint (us1, us2, au, fra, etc.) - default: us2
- `--accessid`: Access ID for authentication
- `--accesskey`: Access key for authentication
- `--limit`: Maximum number of items to retrieve - default varies by script
- `--output-format`: Output format (table, json, details, summary)

## Output Formats

### Table Format (Default)

Clean, human-readable tabular output suitable for terminal viewing:

```
ID                   Name                     Enabled  Created    
-------------------- ------------------------ -------- ------------
abc123...            User Login Rule          Yes      2024-01-15
def456...            Network Anomaly          No       2024-01-10
```

### JSON Format

Machine-readable JSON output for integration with other tools:

```json
[
  {
    "id": "abc123...",
    "name": "User Login Rule",
    "enabled": true,
    "createdAt": "2024-01-15T10:30:00Z"
  }
]
```

### Details Format

Comprehensive information with all available fields:

```
Rule Details
================================================================================
ID: abc123...
Name: User Login Rule
Enabled: Yes
Severity: High
Description: Detects suspicious login patterns
Expression: _sourceCategory contains "authentication" and ...
```

### Summary Format

Statistical overview with grouped information:

```
=== Detection Rules Summary ===
Total Rules: 125
Enabled: 98
Disabled: 27

Rules by Severity:
  High: 15
  Medium: 45
  Low: 65
```

## Popular Use Cases and Examples

### SOC Operations

**Daily rule review:**
```bash
# Get overview of user-created rules
./get_rules.py --query='ruleSource:"user"' --output-format summary

# Check recent high-severity insights
./query_insights.py --severity High --limit 20
```

**Incident investigation:**
```bash
# Find rules related to specific attack vector
./get_rules.py --query "authentication" --output-format details

# Get insights for specific entity
./query_insights.py --query "entity:suspicious-host.domain.com"
```

### Rule Management

**Before rule deployment:**
```bash
# Review existing user rules
./get_rules.py --query='ruleSource:"user"' --limit 100

# Check current tuning expressions
./get_rule_tuning_expressions.py --filter-enabled
```

**Performance optimization:**
```bash
# Find rules with many tuning expressions
./rule_tuning_details.py --search-term "rule-name" --show-expressions

# Review entity criticality settings
./get_entity_criticality.py --output-format details
```

### Configuration Audit

**Export configurations for backup:**
```bash
# Export all rules
./get_rules.py --output-format json --limit 1000 > rules_backup.json

# Export log mappings
./get_log_mappings.py --output-format json > mappings_backup.json

# Export tag schemas
./get_tag_schemas.py --output-format json > schemas_backup.json
```

**Review security configuration:**
```bash
# Check enabled context actions
./get_context_actions.py --filter-enabled --output-format details

# Review entity group configurations
./get_entity_groups.py --filter-enabled --output-format details
```

### Integration Examples

**Data analysis pipeline:**
```bash
# Export insights for analysis
./query_insights.py --output-format json --limit 500 > insights_data.json

# Get rule statistics
./get_rules.py --output-format summary > rule_stats.txt

# Export tuning expressions
./get_rule_tuning_expressions.py --output-format json > tuning_data.json
```

**Monitoring and alerting:**
```bash
# Check for new high-severity insights
./get_insights_list.py --query "severity:High" --limit 10

# Monitor rule performance
./get_rules.py --filter-enabled --output-format summary
```

## Advanced Examples

### Multi-step Analysis

**Investigate high-noise rules:**
```bash
# 1. Find rules with multiple tuning expressions
./rule_tuning_details.py --search-term "Failed Authentication" --show-expressions

# 2. Get detailed rule information
./get_rules.py --rule-id "rule-id-from-step-1" --output-format details

# 3. Check recent insights from this rule
./query_insights.py --query "ruleName:Failed Authentication" --limit 20
```

**Environment assessment:**
```bash
# 1. Get overview of all configurations
./get_rules.py --output-format summary
./get_log_mappings.py --output-format vendors
./get_tag_schemas.py --output-format summary

# 2. Check entity configurations
./get_entity_groups.py --output-format summary
./get_entity_criticality.py --output-format summary

# 3. Review context actions and custom insights
./get_context_actions.py --output-format summary
./get_custom_insights.py --output-format summary
```

## Error Handling

The scripts include comprehensive error handling for common issues:

- **Authentication Errors**: Clear messages about credential problems
- **API Errors**: HTTP status codes and detailed error messages  
- **Network Issues**: Timeout and connection error handling
- **Data Parsing**: Graceful handling of unexpected response formats

## Tips and Best Practices

1. **Start Small**: Use `--limit 10` when testing to avoid overwhelming output
2. **Use Appropriate Endpoints**: Make sure you're using the correct endpoint for your deployment
3. **Leverage Search**: The search functionality is powerful for finding specific items
4. **Export Data**: Use JSON format for data analysis and integration with other tools
5. **Regular Reviews**: Use summary formats to monitor system health and configuration
6. **Combine Scripts**: Chain multiple scripts together for comprehensive analysis

## Troubleshooting

### Common Issues

**"Authentication failed"**
- Check your SUMO_ACCESS_ID and SUMO_ACCESS_KEY environment variables
- Verify the credentials have Cloud SIEM access
- Ensure you're using the correct endpoint (--endpoint parameter)

**"No results found"**
- Try removing filters to see all items
- Check if you have the necessary permissions
- Verify the search query syntax

**"API request failed"**
- Check your network connection
- Verify the endpoint is correct for your deployment
- Some endpoints may have rate limiting - try reducing --limit

### Performance Tips

**For large datasets:**
- Use `--limit` to control response size
- Use `--offset` for pagination
- Consider using summary format for overview

**For regular monitoring:**
- Create shell scripts that combine multiple commands
- Use JSON output for automated processing
- Set up scheduled runs for regular reporting

## Contributing

To contribute additional examples:

1. Follow the existing script structure and error handling patterns
2. Include comprehensive help text and usage examples
3. Test with various endpoints and scenarios
4. Update this README with your new script documentation
5. Ensure scripts follow the project's coding standards (ruff, black)

## Getting Help

For SDK-specific issues:
- Check the main project README
- Review the API documentation at https://api.sumologic.com/docs/sec/
- File issues at the project GitHub repository

For Cloud SIEM questions:
- Consult Sumo Logic Cloud SIEM documentation
- Contact Sumo Logic support