# Test Scenarios

This directory contains test scenarios for the schema validator. Each scenario is contained in its own directory and consists of:

- `scenario.json`: Describes the test case and expected results
- `schema.json`: The schema file for this test
- `data.json`: The data file that will be validated against the schema

## Adding New Scenarios

1. Create a new directory under `scenarios/` with a descriptive name
2. Create the three required files:
   - `scenario.json`: Define test metadata and expected results
   - `schema.json`: The schema to test against
   - `data.json`: The data to validate

### scenario.json format:
```json
{
    "name": "Human readable name",
    "description": "Detailed description of what this scenario tests",
    "expected_results": {
        "structural_errors": [],
        "warnings": [
            "Expected warning message 1",
            "Expected warning message 2"
        ],
        "errors": [
            "Expected error message 1"
        ],
        "info": [
            "Expected info message 1"
        ]
    },
    "schema_file": "schema.json",
    "data_file": "data.json"
}
```

## Current Scenarios

1. schema_validation
   - Tests schema structure validation
   - Verifies required keys, data types, and nested structures

2. data_validation
   - Tests data structure validation
   - Verifies JSON format and basic data structure

3. table_validation
   - Tests table name validation
   - Verifies tables in data exist in schema
   - Reports missing tables as warnings

4. column_validation
   - Tests column name validation
   - Verifies columns in data exist in schema
   - Reports undefined columns as warnings

5. type_validation
   - Tests data type validation
   - Verifies values match their defined column types
   - Handles type conversion where appropriate

6. foreign_key_validation
   - Tests foreign key relationships
   - Verifies referenced tables and values exist
   - Handles both single values and arrays
   - Supports nullable foreign keys

7. property_validation
   - Tests property constraints on columns
   - Supports multiple property types:
     - regex: Pattern matching for string values
     - nullable: Whether null values are allowed
     - NoLessThan: Minimum numeric value (inclusive)
     - NoGreaterThan: Maximum numeric value (inclusive)
   - Reports validation failures as errors

Each scenario directory contains specific test cases for these validation types, with both valid and invalid data to ensure proper validation behavior.
