# main.py

import argparse
import json
import datetime
import re

from validators.type_validators import column_type_validator
from validators.property_validators import regex_validator, nullable_validator, no_less_than_validator, no_greater_than_validator

from utils.logger import SchemaValidatorLogger

def validate_schema(schema, logger):
    """Validate schema structure"""
    has_errors = False
    
    # Check required schema keys
    required_schema_keys = ['version', 'release_date', 'commentary', 'tables', 'table_types',
                            'column_types', 'relationship_types', 'property_types']
    for key in required_schema_keys:
        if key not in schema:
            logger.add_message(f"Schema is missing required key: '{key}'", 'structural_error')
            has_errors = True
            continue

    # Check tables is a list
    if not isinstance(schema.get('tables', None), list):
        logger.add_message("'tables' should be a list in the schema", 'structural_error')
        has_errors = True
    else:
        # Validate each table
        for table in schema['tables']:
            required_table_keys = ['uuid', 'name', 'description', 'type', 'pos_x', 'pos_y', 'columns']
            for key in required_table_keys:
                if key not in table:
                    logger.add_message(f"Table is missing required key: '{key}'", 'structural_error')
                    has_errors = True
                    continue

            if not isinstance(table.get('columns', None), list):
                logger.add_message(f"'columns' should be a list in table '{table['name']}'", 'structural_error')
                has_errors = True
            else:
                # Validate each column
                for column in table['columns']:
                    required_column_keys = ['uuid', 'name', 'description', 'type', 'relationship', 'properties']
                    for key in required_column_keys:
                        if key not in column:
                            logger.add_message(f"Column is missing required key: '{key}' in table '{table['name']}'", 'structural_error')
                            has_errors = True
                            continue

                    if column.get('relationship') is not None and not isinstance(column['relationship'], list):
                        logger.add_message(f"'relationship' should be a list or None in column '{column['name']}'", 'structural_error')
                        has_errors = True

                    if column.get('properties') is not None and not isinstance(column['properties'], list):
                        logger.add_message(f"'properties' should be a list or None in column '{column['name']}'", 'structural_error')
                        has_errors = True

    # Validate type sections
    type_sections = ['table_types', 'column_types', 'relationship_types', 'property_types']
    for section in type_sections:
        if not isinstance(schema.get(section, None), list):
            logger.add_message(f"'{section}' should be a list in the schema", 'structural_error')
            has_errors = True
            continue
            
        for item in schema[section]:
            required_type_keys = ['uuid', 'name', 'description']
            if section == 'table_types':
                required_type_keys.append('color')
            for key in required_type_keys:
                if key not in item:
                    logger.add_message(f"Item in '{section}' is missing required key: '{key}'", 'structural_error')
                    has_errors = True

    if has_errors:
        raise ValueError("Schema validation failed. Check structural errors for details.")

def validate_data(data, logger):
    """Validate data structure"""
    has_errors = False
    
    if not isinstance(data, dict):
        logger.add_message("Data must be a dictionary", 'structural_error')
        raise ValueError("Data must be a dictionary")
        
    for class_name, objects in data.items():
        if not isinstance(objects, list):
            logger.add_message(f"The value for class '{class_name}' should be a list of objects", 'structural_error')
            has_errors = True
            continue  # Skip object validation if the class value isn't a list

        for obj in objects:
            if not isinstance(obj, dict):
                logger.add_message(f"Each object in class '{class_name}' should be a dictionary", 'structural_error')
                has_errors = True
                
                
    if has_errors:
        raise ValueError("Data validation failed. Check structural errors for details.")

def validate_table_names(data, schema, logger):
    """Validate table names in data against schema"""
    schema_table_names = [tbl['name'] for tbl in schema['tables']]
    
    # Check for classes that are not in the schema
    for obj_class in data:
        if obj_class not in schema_table_names:
            logger.add_message(f"The Class '{obj_class}' is not found in schema", 'warning')
            
            
    # Check for classes that are in the schema but not in the data
    for schema_table in schema['tables']:
        if schema_table['name'] not in data:
            logger.add_message(f"The Class '{schema_table['name']}' is not found in data", 'info')
            

   


def validate_property(col_name, value, property):

    property_types = {
        "regex": regex_validator,
        "nullable": nullable_validator
    }

    prop_type_uuid = property['type']
    prop_value = property['value']
    prop_type_name = next((p['name'] for p in schema['property_types'] if p['uuid'] == prop_type_uuid), None)

    if prop_type_name in property_types:
        if not property_types[prop_type_name](value, prop_value):
            error_msg = f"Validation failed for {col_name} with value {value} against property {prop_type_name} with condition {prop_value}"
            logger.add_message(error_msg, 'error')

     


def validate_column_names(data, schema, logger):
    """Validate column names in data against schema"""
    # Column Names (Columns that aren't found in the Schema) (Warning)
    for obj_class in data:
        # Only check if the table is in the schema
        if obj_class not in [schema_table['name'] for schema_table in schema['tables']]:
            continue

        # Get the corresponding schema table
        schema_table = [schema_table for schema_table in schema['tables'] if schema_table['name'] == obj_class][0]

        # Get the columns of the table from the schema
        expected_columns = [column['name'] for column in schema_table['columns']]

        # Iterate over the objects in the data
        for obj in data[obj_class]:
            # Check if there are columns in the data that are not in the schema
            for attribute, value in obj.items():
                if attribute not in expected_columns:
                    logger.add_message(f'The attribute {obj_class}.{attribute} is not a valid column in the schema', 'warning')

            # Check if there are columns in the schema that are not in the data (these will just be info)
            for column in expected_columns:
                if column not in obj:
                    logger.add_message(f"{obj_class}.{column} not found in data", 'info')

def validate_column_types(data, schema, logger):
    """Validate column types in data against schema"""
    for obj_class in data:
        # Only check if the table is in the schema
        if obj_class in [schema_table['name'] for schema_table in schema['tables']]:
            # Get the corresponding schema table
            corresponding_schema_table = next(schema_table for schema_table in schema['tables'] if schema_table['name'] == obj_class)

            # Iterate over the objects of this Class type
            for obj in data[obj_class]:
                # Iterate over each of the attributes for the given object and their values
                for attribute, value in obj.items():
                    # Only check the attribute if found in the schema and value is not None
                    if attribute in [column['name'] for column in corresponding_schema_table['columns']] and value is not None:
                        # Get the corresponding attribute/column definition from the Schema
                        corresponding_schema_column = next(schema_column for schema_column in corresponding_schema_table['columns'] if schema_column['name'] == attribute)
                        # Get the expected column/attribute type from the schema
                        column_type_uuid = corresponding_schema_column['type']
                        column_type_name = next(column['name'] for column in schema['column_types'] if column['uuid'] == column_type_uuid)

                        # Use the validator function
                        column_type_validator(attribute, value, column_type_name, logger)

def validate_foreign_keys(data, schema, logger):
    """Validate foreign key relationships in data against schema"""
    # Track which warnings we've already added to avoid duplicates
    added_warnings = set()

    for obj_class in data:
        # Only check if the table is in the schema
        if obj_class not in [schema_table['name'] for schema_table in schema['tables']]:
            continue

        # Get the corresponding schema table
        corresponding_schema_table = [schema_table for schema_table in schema['tables'] if schema_table['name'] == obj_class][0]

        # Iterate over the objects in the data
        for obj in data[obj_class]:
            # Only verify the attributes that are in the schema
            for attribute, value in obj.items():
                # Skip if value is None (NULL)
                if value is None:
                    continue
                    
                # Get the corresponding schema column if it exists
                schema_column = next((col for col in corresponding_schema_table['columns'] if col['name'] == attribute), None)
                if not schema_column:
                    continue

                # Check if the column is a foreign key (relationship is not null)
                if schema_column['relationship'] is not None:
                    # Iterate over the relationships
                    for relationship in schema_column['relationship']:
                        # Get the related table and column from the schema
                        related_table_uuid = relationship['table_uuid']
                        related_column_uuid = relationship['column_uuid']

                        # Get the related table and column name from the schema
                        related_table_name = [schema_table['name'] for schema_table in schema['tables'] if schema_table['uuid'] == related_table_uuid][0]
                        related_column_name = [column['name'] for schema_table in schema['tables'] if schema_table['uuid'] == related_table_uuid for column in schema_table['columns'] if column['uuid'] == related_column_uuid][0]

                        # Check to see that the related table exists
                        warning_msg = f"Related table '{related_table_name}' not found in data for foreign key '{attribute}' in table '{obj_class}'"
                        if related_table_name not in data and warning_msg not in added_warnings:
                            logger.add_message(warning_msg, 'warning')
                            added_warnings.add(warning_msg)
                            continue

                        # Handle both single values and arrays
                        values_to_check = value if isinstance(value, list) else [value]

                        # Check each value
                        for single_value in values_to_check:
                            # Skip if value is None
                            if single_value is None:
                                continue
                                
                            related_object_found = False
                            
                            # Iterate over the related objects
                            if related_table_name in data:
                                for related_obj in data[related_table_name]:
                                    # Check to see that the related column exists
                                    if related_column_name not in related_obj:
                                        continue
                                    
                                    # Check to see that the related column value exists in the related table
                                    if single_value == related_obj[related_column_name]:
                                        related_object_found = True
                                        break

                                if not related_object_found:
                                    warning_msg = f"The object {obj_class}.{attribute} with value {single_value} is not related to any {related_table_name}.{related_column_name} in the data"
                                    if warning_msg not in added_warnings:
                                        logger.add_message(warning_msg, 'warning')
                                        added_warnings.add(warning_msg)


def validate_properties(data, schema, logger):
    """Validate properties for all columns in the data against schema"""
    from validators.property_validators import (
        regex_validator, 
        nullable_validator,
        no_less_than_validator,
        no_greater_than_validator
    )

    # Map property types to their validators and clean names
    property_validators = {
        'regex-prop': ('regex', regex_validator),
        'nullable-prop': ('nullable', nullable_validator),
        'no-less-than-prop': ('NoLessThan', no_less_than_validator),
        'no-greater-than-prop': ('NoGreaterThan', no_greater_than_validator)
    }

    for obj_class in data:
        if obj_class not in [schema_table['name'] for schema_table in schema['tables']]:
            continue

        corresponding_schema_table = [schema_table for schema_table in schema['tables'] if schema_table['name'] == obj_class][0]

        for obj in data[obj_class]:
            for attribute, value in obj.items():
                schema_column = next((col for col in corresponding_schema_table['columns'] if col['name'] == attribute), None)
                if not schema_column or not schema_column['properties']:
                    continue

                for property in schema_column['properties']:
                    property_type = property['type']
                    property_value = property['value']

                    if property_type in property_validators:
                        clean_name, validator = property_validators[property_type]
                        if not validator(value, property_value):
                            # Special case for regex to avoid complex pattern in error message
                            if property_type == 'regex-prop':
                                logger.add_message(
                                    f"Validation failed for {attribute} with value {value} against property {clean_name}",
                                    'error'
                                )
                            else:
                                logger.add_message(
                                    f"Validation failed for {attribute} with value {value} against property {clean_name} with condition {str(property_value).lower()}",
                                    'error'
                                )

# Start of the main script
if __name__ == "__main__":
    import sys

    parser = argparse.ArgumentParser(description='Validate data against schema.')
    parser.add_argument('schema_file', type=str, help='Path to the schema JSON file')
    parser.add_argument('data_file', type=str, help='Path to the data JSON file')
    args = parser.parse_args()

    logger = SchemaValidatorLogger()

    try:
        with open(args.schema_file, 'r') as f:
            schema = json.load(f)
    except Exception as e:
        logger.add_message(f"Error reading schema file: {e}", 'error')
        sys.exit(1)

    try:
        with open(args.data_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        logger.add_message(f"Error reading data file: {e}", 'error')
        sys.exit(1)

    # Validate schema and data formats
    try:
        validate_schema(schema, logger)
    except ValueError as e:
        logger.add_message(f"Schema validation error: {e}", 'error')
        sys.exit(1)

    try:
        validate_data(data, logger)
    except ValueError as e:
        logger.add_message(f"Data validation error: {e}", 'error')
        sys.exit(1)

    # Table Names
    validate_table_names(data, schema, logger)

    # Column Names (Columns that aren't found in the Schema) (Warning)
    validate_column_names(data, schema, logger)

    # Column Types (Warning if convertible like String to Float otherwise Error)
    validate_column_types(data, schema, logger)

    # Foreign Key Checks (Warning)
    validate_foreign_keys(data, schema, logger)

    # Property Checks
    validate_properties(data, schema, logger)

    # At the end, print or save the logger messages
    logger.print_messages()
