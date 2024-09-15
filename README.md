# Schema and Data Validator

This script validates a digital twin data file against a specified schema, ensuring:

- Correct schema file formatting
- Correct data file formatting
- Data conformity to schema rules (data types, relationships, and properties)

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Schema and Data Format](#schema-and-data-format)
- [Validation Process](#validation-process)
- [Usage](#usage)
- [Logging](#logging)
- [Examples](#examples)
- [License](#license)

## Installation

Ensure you have Python 3.x installed. Then install the required libraries:

## Schema and Data Format

### Schema Format

The schema JSON file should be formatted as follows:

```json
{
    "version": "version of the cyber data schema",
    "release_date": "date of the release",
    "commentary": "commentary about the specific release",
    "tables": [
        {
            "uuid": "uuid of the table",
            "name": "name of the table",
            "description": "description of the table",
            "type": "type of the table",
            "pos_x": "x-coordinate position",
            "pos_y": "y-coordinate position",
            "columns": [
                {
                    "uuid": "uuid of the column",
                    "name": "name of the column",
                    "description": "description of the column",
                    "type": "type of the column",
                    "relationship": [
                        {
                            "uuid": "uuid of the relationship",
                            "type": "type of the relationship",
                            "table_uuid": "uuid of the related table",
                            "column_uuid": "uuid of the related column",
                            "description": "description of the relationship"
                        }
                    ],
                    "properties": [
                        {
                            "uuid": "uuid of the property",
                            "type": "type of the property",
                            "value": "value of the property"
                        }
                    ]
                }
            ]
        }
    ],
    "table_types": [
        {
            "uuid": "uuid of the table type",
            "name": "name of the table type",
            "description": "description of the table type",
            "color": "color of the table type"
        }
    ],
    "column_types": [
        {
            "uuid": "uuid of the column type",
            "name": "name of the column type",
            "description": "description of the column type"
        }
    ],
    "relationship_types": [
        {
            "uuid": "uuid of the relationship type",
            "name": "name of the relationship type",
            "description": "description of the relationship type"
        }
    ],
    "property_types": [
        {
            "uuid": "uuid of the property type",
            "name": "name of the property type",
            "description": "description of the property type"
        }
    ]
}
```

### Data Format

The data JSON file (digital twin data) should be formatted as follows:

```json
{
    "Class1": [
        {
            "Property1": "Value1",
            "Property2": "Value2"
        },
        {
            "Property1": "Value1",
            "Property2": "Value2"
        }
    ],
    "Class2": [
        {
            "Property3": "Value3",
        },
        {
            "Property3": "Value3",
            "Property4": "Value4"
        }
    ]
}
```

## Usage

Run the validator script with the schema and data files as command-line arguments:

```bash
python run.py path/to/schema.json path/to/data.json
```

## Validation Process

The script performs the following validation steps:

    Schema Validation: Ensures that the schema file is correctly formatted and contains all required keys and structures.

    Data Validation: Ensures that the data file is correctly formatted and matches the structure expected by the schema.

    Table/Class Names Check: Checks if all classes (tables) in the data are defined in the schema. Logs warnings for any classes not found in the schema.

    Column/Attribute Names Check: For each class, checks if all attributes (columns) in the data objects are defined in the schema. Logs warnings for any attributes not found in the schema.

    Foreign Key Checks: Validates relationships between objects according to foreign keys defined in the schema. Logs warnings if related objects are missing.

    Column Types Validation: Checks that each attribute's value matches the expected data type defined in the schema. If the value can be converted to the correct type, logs a warning. If not, logs an error.

    Property Checks: Validates properties like nullable and regex constraints defined in the schema for each attribute.

## Logging

The script uses a logger to collect messages at different severity levels:

    INFO: General informational messages.
    WARNING: Non-critical issues that may need attention.
    ERROR: Critical issues that prevent validation from proceeding.

At the end of the validation, the script prints all logged messages.

## Requirements

    Python 3.x
    tqdm library for progress bars

Install the required libraries using:

```bash
pip install tqdm
```

## Examples

### Running the Validator

```bash
python run.py schema.json data.json
```
Sample Output

```sql

Table/Class Names: 100%|██████████| 2/2 [00:00<00:00, 1000.00it/s]
Column/Attribute Names: 100%|██████████| 2/2 [00:00<00:00, 500.00it/s]
Foreign Keys: 100%|██████████| 2/2 [00:00<00:00, 500.00it/s]
Column Types: 100%|██████████| 2/2 [00:00<00:00, 500.00it/s]
Property Types: 100%|██████████| 2/2 [00:00<00:00, 500.00it/s]
INFO: Class1.Property2 not found in data
WARNING: The attribute Class1.InvalidAttribute is not a valid column in the schema
ERROR: Value 'invalid_date' is not compatible with DATE type and cannot be converted. time data 'invalid_date' does not match format '%Y-%m-%d'
```

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

