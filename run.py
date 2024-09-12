import tqdm
import json

from validators.type_validators import column_type_validator
from validators.property_validators import regex_validator, nullable_validator

from utils.logger import SchemaValidatorLogger

schema = json.load(open('schema.json'))

data = json.load(open('data.json'))
    

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



logger = SchemaValidatorLogger()


# Table Names (Tables that aren't found in the Schema) (Warning) 
for obj_class in tqdm.tqdm(data, desc='Table/Class Names'):
    # Check if there is a table in the data that is not in the schema
    if obj_class not in [schema_table['name'] for schema_table in schema['tables']]:
        logger.add_message(f"The Class '{obj_class}' is not found in schema", 'warning')
        

# Column Names (Columns that aren't found in the Schema) (Warning)
for obj_class in tqdm.tqdm(data, desc='Column/Attribute Names'):
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
                              
  
# Foreign Key Checks (Warning)
for obj_class in tqdm.tqdm(data, desc='Foreign Keys'):
    # Only check if the table is in the schema
    if obj_class not in [schema_table['name'] for schema_table in schema['tables']]:
        continue

    # Get the corresponding schema table
    corresponding_schema_table = [schema_table for schema_table in schema['tables'] if schema_table['name'] == obj_class][0]

    # Get the columns of the table from the schema
    expected_columns = [column['name'] for column in corresponding_schema_table['columns']]

    # Iterate over the objects in the data
    for obj in data[obj_class]:
        # Only verify the attributes that are in the schema
        for attribute, value in obj.items():
            if attribute in expected_columns:
                # Get the corresponding schema column
                corresponding_schema_column = [schema_column for schema_column in corresponding_schema_table['columns'] if schema_column['name'] == attribute][0]

                # Check if the column is a foreign key (relationship is not null)
                if corresponding_schema_column['relationship'] is not None:
                    
                    # Iterate over the relationships
                    for relationship in corresponding_schema_column['relationship']:
                        # Get the related table and column from the schema
                        related_table_uuid = relationship['table_uuid']
                        related_column_uuid = relationship['column_uuid']
                        
                        # Get the related table and column name from the schema
                        related_table_name = [schema_table['name'] for schema_table in schema['tables'] if schema_table['uuid'] == related_table_uuid][0]
                        related_column_name = [column['name'] for schema_table in schema['tables'] for column in schema_table['columns'] if column['uuid'] == related_column_uuid][0]

                        # Check to see if the related object exists in the data for this relationship
                        related_object_found = False
                        
                        # Check to see that the related table exists
                        if related_table_name not in data:
                            logger.add_message(f"Related table '{related_table_name}' not found in data for foreign key '{attribute}' in table '{obj_class}'", 'warning')
                        else:
                            # Iterate over the related objects
                            for related_obj in data[related_table_name]:
                                # Check to see that the related column exists
                                if related_column_name not in related_obj:
                                    # We don't put a warning here because it is just a single object that maybe intentionally doesn't have the related column because another object of the same class does have it
                                    pass
                                else:
                                    # Check to see that the related column value exists in the related table
                                    if obj[attribute] == related_obj[related_column_name]:
                                        related_object_found = True
                                        break  
                        if not related_object_found:
                            logger.add_message(f"The object {obj_class}.{attribute} with value {obj[attribute]} is not related to any {related_table_name}.{related_column_name} in the data", 'warning')
                            
                            

# Column Types (Warning if convertible like String to Float otherwise Error)
for obj_class in tqdm.tqdm(data, desc='Column Types'):
    # Only check if the table is in the schema
    if obj_class in [schema_table['name'] for schema_table in schema['tables']]:
        
        # Get the corresponding schema table
        corresponding_schema_table = next(schema_table for schema_table in schema['tables'] if schema_table['name'] == obj_class)

        # Iterate over the objects of this Class type in the digital twin
        for obj in data[obj_class]:
            # Iterate over each of the attributes for the given object and their values
            for attribute, value in obj.items():
                # Only check the attribute if found in the schema
                if attribute in [column['name'] for column in corresponding_schema_table['columns']]:
                    # Get the corresponding attribute/column definition from the Schema
                    corresponding_schema_column = next(schema_column for schema_column in corresponding_schema_table['columns'] if schema_column['name'] == attribute)
                    # Get the expected column/attribute type from the schema
                    column_type_uuid = corresponding_schema_column['type']
                    column_type_name = next(column['name'] for column in schema['column_types'] if column['uuid'] == column_type_uuid)

                    # Use the validator function
                    column_type_validator(attribute, value, column_type_name, logger)
              

# Property Checks
for obj_class in tqdm.tqdm(data, desc='Property Types'):
    # Only check if the table is in the schema
    if obj_class in [schema_table['name'] for schema_table in schema['tables']]:
        
        # Get the corresponding schema table
        corresponding_schema_table = next(schema_table for schema_table in schema['tables'] if schema_table['name'] == obj_class)

        # Iterate over the objects of this Class type in the digital twin
        for obj in data[obj_class]:
            # Iterate over each of the attributes for the given object and their values
            for attribute, value in obj.items():
                # Only check the attribute if found in the schema
                if attribute in [column['name'] for column in corresponding_schema_table['columns']]:
                    # Get the corresponding attribute/column definition from the Schema
                    corresponding_schema_column = next(schema_column for schema_column in corresponding_schema_table['columns'] if schema_column['name'] == attribute)
                    
                    # Validate each property for the column
                    if 'properties' in corresponding_schema_column:
                        # Make sure the properties are not None
                        if corresponding_schema_column['properties']:
                            for property in corresponding_schema_column['properties']:
                                validate_property(attribute, value, property)
                                
                    
                    
# print(f'INFO:')                            
# for info in logger.info:
#     print(info)
    
# print()

# print(f'WARNINGS:')
# for warning in logger.warnings:
#     print(warning)
    
# print()

# print(f'ERRORS:')
# for error in logger.errors:
#     print(error)