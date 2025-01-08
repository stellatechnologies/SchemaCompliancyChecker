# Schema and Data Validator

A web application and command-line tool that validates digital twin data files against a specified schema, ensuring:

- Correct schema file formatting
- Correct data file formatting
- Data conformity to schema rules (data types, relationships, and properties)

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Web Interface](#web-interface)
- [Command Line Interface](#command-line-interface)
- [Schema and Data Format](#schema-and-data-format)
- [Validation Process](#validation-process)
- [Logging](#logging)
- [Testing](#testing)
- [License](#license)

## Installation

1. Ensure you have Python 3.x installed
2. Clone this repository
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Web Interface

Start the web application:

```bash
python app.py
```

Then navigate to `http://localhost:5000` in your browser. The web interface allows you to:
- Upload schema and data files
- View real-time validation progress
- See validation results with color-coded messages
- Download validation reports

### Command Line Interface

Run the validator script directly:

```bash
python main.py path/to/schema.json path/to/data.json
```

## Schema and Data Format

### Schema Format
```json
{
    "version": "1.0",
    "release_date": "2024-03-20",
    "commentary": "Schema description",
    "tables": [
        {
            "uuid": "table-uuid",
            "name": "TableName",
            "description": "Table description",
            "type": "entity",
            "pos_x": "0",
            "pos_y": "0",
            "columns": [
                {
                    "uuid": "column-uuid",
                    "name": "column_name",
                    "description": "Column description",
                    "type": "column-type-uuid",
                    "relationship": null,
                    "properties": [
                        {
                            "type": "property-type-uuid",
                            "value": "property-value"
                        }
                    ]
                }
            ]
        }
    ],
    "table_types": [...],
    "column_types": [...],
    "relationship_types": [...],
    "property_types": [...]
}
```

### Data Format
```json
{
    "TableName": [
        {
            "column_name": "value",
            "another_column": "another_value"
        }
    ]
}
```

## Validation Process

The validator performs these checks in sequence:

1. **Schema Structure Validation**
   - Verifies required keys and correct data types
   - Validates nested structures and relationships

2. **Data Structure Validation**
   - Ensures proper JSON formatting
   - Validates basic data structure requirements

3. **Table Name Validation**
   - Checks if data tables exist in schema
   - Reports missing or extra tables

4. **Column Name Validation**
   - Verifies column names against schema
   - Reports undefined or missing columns

5. **Column Type Validation**
   - Validates data types of values
   - Attempts type conversion where possible

6. **Foreign Key Validation**
   - Checks relationship integrity
   - Validates referenced data exists

7. **Property Validation**
   - Validates regex patterns
   - Checks nullable constraints
   - Verifies numeric bounds (min/max)

## Logging

Messages are categorized into four levels:
- **Structural Errors**: Fatal issues in basic structure
- **Errors**: Validation failures that need attention
- **Warnings**: Potential issues to review
- **Info**: Informational messages

## Testing

Run the test suite:

```bash
python -m unittest discover tests
```

Test scenarios cover:
- Schema validation
- Data validation
- Table validation
- Column validation
- Type validation
- Foreign key validation
- Property validation

## Validation Matrix

| Validation Type | Scenario | Structural<br>Error | Error | Warning | Info | Example/Explanation |
|----------------|----------|:------------------:|:------:|:-------:|:----:|-------------------|
| **Schema Structure** | Missing required key | ✓ | | | | "Schema is missing required key: 'tables'" - Schema must contain all required top-level keys |
| | Invalid data type | ✓ | | | | "'tables' should be a list in the schema" - Schema elements must be of correct type |
| **Data Structure** | Invalid JSON format | ✓ | | | | "Data must be a dictionary" - Data file must be valid JSON object |
| | Invalid object format | ✓ | | | | "Each object in class 'User' should be a dictionary" - Table entries must be objects |
| **Table Names** | Table in data missing from schema | | | ✓ | | "The Class 'User' is not found in schema" - Data contains table not defined in schema |
| | Table in schema missing from data | | | | ✓ | "The Class 'User' is not found in data" - Optional table defined in schema but not in data |
| **Column Names** | Column in data missing from schema | | | ✓ | | "The attribute User.email is not a valid column" - Data contains undefined column |
| | Column in schema missing from data | | | | ✓ | "User.email not found in data" - Optional column not present in data |
| **Column Types** | Invalid type, not convertible | | ✓ | | | "Value 'abc' cannot be converted to INT type" - String in numeric field |
| | Array type conversion | | | | ✓ | "Value '[1,2,3]' was converted to Array(INT)" - Valid array conversion |
| | Other type conversion | | | ✓ | | "Value '123' was converted from STRING to INT" - Automatic type conversion |
| **Foreign Keys** | Referenced table missing | | | ✓ | | "Related table 'Department' not found for foreign key 'dept_id'" - Missing referenced table |
| | Referenced value missing | | | ✓ | | "User.dept_id with value 5 not related to any Department.id" - Invalid reference |
| **Properties** | Invalid regex pattern | | ✓ | | | "email 'invalid-email' against property regex" - Email doesn't match pattern |
| | Non-nullable field is null | | ✓ | | | "name with value None against property nullable with condition false" - Required field is null |
| | Value below minimum | | ✓ | | | "age with value 15 against property NoLessThan with condition 18" - Age below minimum |
| | Value above maximum | | ✓ | | | "score with value 105 against property NoGreaterThan with condition 100" - Score exceeds maximum |

Message Types:
- **Structural Error**: Fatal issues that prevent further validation
- **Error**: Validation failures that must be fixed
- **Warning**: Potential issues that should be reviewed
- **Info**: Informational messages about optional elements

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

