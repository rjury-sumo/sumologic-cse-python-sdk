# Cloud SIEM Python SDK - Example Scripts

This directory contains example scripts demonstrating how to use the Sumo Logic Cloud SIEM Python SDK with various API endpoints, particularly focusing on the new v0.2.0+ features.

## Rule Tuning Expressions Examples

Rule tuning expressions provide a way to fine-tune rule behavior without modifying the rules directly. They allow you to add conditions that exclude certain events from triggering rules, helping reduce false positives and noise.

### Scripts Available

#### `get_rule_tuning_expressions.py`
**Purpose**: Retrieve and display rule tuning expressions in various formats

**Features**:
- List all rule tuning expressions
- Filter by enabled/disabled status
- Multiple output formats (table, JSON, summary)
- Pagination support

**Usage**:
```bash
# Basic usage - show all expressions in table format
python get_rule_tuning_expressions.py

# Show only enabled expressions
python get_rule_tuning_expressions.py --filter-enabled

# Output as JSON for further processing
python get_rule_tuning_expressions.py --output-format json

# Show summary statistics
python get_rule_tuning_expressions.py --output-format summary --limit 200

# Use specific endpoint
python get_rule_tuning_expressions.py --endpoint us1
```

#### `rule_tuning_details.py`
**Purpose**: Get detailed information about specific rule tuning expressions

**Features**:
- Get detailed view of specific rule tuning expression by ID
- Search expressions by name, description, or rule name
- Display actual expression syntax and logic
- Show associated rule information and audit trail

**Usage**:
```bash
# Get details for a specific expression
python rule_tuning_details.py --expression-id "12345-abcde-67890"

# Search for expressions containing "failed login"
python rule_tuning_details.py --search-term "failed login"

# Show expression syntax and logic
python rule_tuning_details.py --show-expressions --search-term "brute force"

# List expressions with search filter
python rule_tuning_details.py --search-term "authentication" --limit 100
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

## Output Formats

### Table Format (Default)
Clean, human-readable tabular output suitable for terminal viewing:
```
ID                   Name                     Enabled  Rule Name              Created    
-------------------- ------------------------ -------- ---------------------- ------------
abc123...            Reduce Login Noise       Yes      Failed Authentication  2024-01-15
def456...            Filter Internal Traffic  No       Network Anomaly        2024-01-10
```

### JSON Format
Machine-readable JSON output for integration with other tools:
```json
[
  {
    "id": "abc123...",
    "name": "Reduce Login Noise",
    "enabled": true,
    "ruleName": "Failed Authentication",
    "expression": "...",
    "createdAt": "2024-01-15T10:30:00Z"
  }
]
```

### Summary Format
Statistical overview with grouped information:
```
=== Rule Tuning Expressions Summary ===
Total Expressions: 25
Enabled: 18
Disabled: 7

Expressions by Rule:
  Failed Authentication: 5 expressions (4 enabled)
  Network Anomaly: 3 expressions (2 enabled)
  ...
```

## Error Handling

The scripts include comprehensive error handling for common issues:

- **Authentication Errors**: Clear messages about credential problems
- **API Errors**: HTTP status codes and detailed error messages  
- **Network Issues**: Timeout and connection error handling
- **Data Parsing**: Graceful handling of unexpected response formats

## Use Cases

### SOC Operations
- **Daily Review**: Use `get_rule_tuning_expressions.py --output-format summary` to get an overview of rule tuning status
- **Troubleshooting**: Use `rule_tuning_details.py --search-term "rule-name"` to find expressions affecting a specific rule
- **Audit**: Use `--output-format json` to export data for compliance reporting

### Rule Management
- **Before Rule Changes**: Review existing tuning expressions that might affect new rule versions
- **After Rule Deployment**: Check if new rules need tuning expressions to reduce noise
- **Performance Optimization**: Identify rules with many tuning expressions that might need consolidation

### Integration Examples
```bash
# Export all tuning expressions for backup
python get_rule_tuning_expressions.py --output-format json --limit 1000 > tuning_backup.json

# Find all expressions for authentication-related rules
python rule_tuning_details.py --search-term "auth" --show-expressions > auth_tuning_review.txt

# Get daily summary for SOC dashboard
python get_rule_tuning_expressions.py --output-format summary --filter-enabled > daily_tuning_summary.txt
```

## Tips and Best Practices

1. **Start Small**: Use `--limit 10` when testing to avoid overwhelming output
2. **Use Search**: The `--search-term` feature is powerful for finding specific expressions
3. **Regular Reviews**: Rule tuning expressions can accumulate over time - regular reviews help maintain efficiency
4. **JSON Export**: Use JSON format for data analysis and integration with other security tools
5. **Endpoint Selection**: Make sure you're using the correct endpoint for your Sumo Logic deployment

## Troubleshooting

### Common Issues

**"Authentication failed"**
- Check your SUMO_ACCESS_ID and SUMO_ACCESS_KEY environment variables
- Verify the credentials have Cloud SIEM access
- Ensure you're using the correct endpoint (--endpoint parameter)

**"No rule tuning expressions found"**
- Rule tuning expressions are optional and may not exist in all environments
- Try removing filters (like --filter-enabled) to see all expressions
- Verify you have the necessary permissions to view rule tuning expressions

**"API request failed"**
- Check your network connection
- Verify the endpoint is correct for your Sumo Logic deployment
- Some endpoints may have rate limiting - try reducing --limit or adding delays

### Getting Help

For SDK-specific issues:
- Check the main project README
- Review the API documentation at https://api.sumologic.com/docs/sec/
- File issues at the project GitHub repository

For Cloud SIEM questions:
- Consult Sumo Logic Cloud SIEM documentation
- Contact Sumo Logic support

## Contributing

To contribute additional examples:
1. Follow the existing script structure and error handling patterns
2. Include comprehensive help text and examples
3. Test with various endpoints and scenarios
4. Update this README with your new script documentation