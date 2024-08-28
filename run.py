import tqdm
import json

schema = json.load(open('schema.json'))

data = json.load(open('data.json'))


info = []
warnings = []
errors = []


# Table Names (Tables that aren't found in the Schema) (Warning) 
for obj_class in data:
    # Check if there is a table in the data that is not in the schema
    if obj_class not in [schema_table['name'] for schema_table in schema['tables']]:
        warnings.append(f"Table '{obj_class}' not found in schema")

print(warnings)


# Column Names (Columns that aren't found in the Schema) (Warning)
for obj_class in data:
    print(f'Checking Class {obj_class}')
    # Only check if the table is in the schema
    if obj_class not in [schema_table['name'] for schema_table in schema['tables']]:
        print(f"Class '{obj_class}' not found in schema")
        continue
     
    # Get the corresponding schema table
    schema_table = [schema_table for schema_table in schema['tables'] if schema_table['name'] == obj_class][0]
    
    print(f'Schema table: {schema_table}')
    # Get the columns of the table from the schema
    expected_columns = [column['name'] for column in schema_table['columns']]
    
    print(f'Expected Columns: {expected_columns}')
    
    # Iterate over the objects in the data
    for obj in data[obj_class]:
        # Check if there are columns in the data that are not in the schema
        for attribute, value in obj.items():
            if attribute not in expected_columns:
                warnings.append(f"Column '{attribute}' not found in schema for table '{obj_class}'")
                print(f"Column '{attribute}' not found in schema for table '{obj_class}'")
                
        # Check if there are columns in the schema that are not in the data (these will just be info)
        for column in expected_columns:
            if column not in obj:
                info.append(f"Column '{column}' not found in data for table '{obj_class}'")
                print(f"Column '{column}' not found in data for table '{obj_class}'")
                
                
# Foreign Key Checks (Error)

                