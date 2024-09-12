# validators/type_validators.py

import datetime
import re

def boolean_converter(x):
    if isinstance(x, bool):
        return x
    if isinstance(x, str):
        normalized_str = x.strip().lower()
        if normalized_str in ('true', '1', 't', 'y', 'yes'):
            return True
        elif normalized_str in ('false', '0', 'f', 'n', 'no'):
            return False
    elif isinstance(x, (int, float)):
        return x != 0
    raise ValueError(f"Cannot convert {x} to boolean.")


def column_type_validator(col_name, col_val, col_type, logger):
    type_mapping = {
        'DATE': {'type': datetime.date, 'convert': lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date()},
        'BOOLEAN': {'type': bool, 'convert': boolean_converter},
        'FLOAT': {'type': float, 'convert': float},
        'INT': {'type': int, 'convert': int},
        'DATETIME': {'type': datetime.datetime, 'convert': lambda x: datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S')},
        'VARCHAR(255)': {'type': str, 'convert': str},
        'Array(VARCHAR(255))': {'type': list, 'convert': lambda x: [str(i) for i in x] if isinstance(x, list) else [str(x)]},
        'BLOB': {'type': bytes, 'convert': bytes}  # Assuming input can be handled as bytes
    }

    expected_type_info = type_mapping.get(col_type)

    if not expected_type_info:
        logger.add_message(f"Unknown column type {col_type} provided for validation.", 'error')
        return

    try:
        if isinstance(col_val, expected_type_info['type']):
            return  # Correct type
        else:
            converted_value = expected_type_info['convert'](col_val)  # Attempt conversion
            
            print(f'Warning: Value {col_val} was converted to {col_type} type.')
            logger.add_message(f"Value '{col_val}' was converted to {col_type} type.", 'warning')
    except (ValueError, TypeError) as e:
        print(f'Error: Value {col_val} is not compatible with {col_type} type and cannot be converted.')
        logger.add_message(f"Error: Value '{col_val}' is not compatible with {col_type} type and cannot be converted. {str(e)}", 'error')