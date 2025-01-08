# validators/type_validators.py

import datetime

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
        'VARCHAR(45)': {'type': str, 'convert': str},
        'Array(VARCHAR(255))': {'type': list, 'convert': lambda x: [str(i) for i in x] if isinstance(x, list) else [str(x)]},
        'Array(INT)': {'type': list, 'convert': lambda x: [int(i) for i in x] if isinstance(x, list) else [int(x)]},
        'Array(FLOAT)': {'type': list, 'convert': lambda x: [float(i) for i in x] if isinstance(x, list) else [float(x)]},
        'Array(BOOLEAN)': {'type': list, 'convert': lambda x: [boolean_converter(i) for i in x] if isinstance(x, list) else [boolean_converter(x)]},
        'Array(DATE)': {'type': list, 'convert': lambda x: [datetime.datetime.strptime(i, '%Y-%m-%d').date() for i in x] if isinstance(x, list) else [datetime.datetime.strptime(x, '%Y-%m-%d').date()]},
        'Array(DATETIME)': {'type': list, 'convert': lambda x: [datetime.datetime.strptime(i, '%Y-%m-%dT%H:%M:%S') for i in x] if isinstance(x, list) else [datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S')]},
        'BLOB': {'type': str, 'convert': str},
        'TINYINT': {'type': int, 'convert': int},
    }

    expected_type_info = type_mapping.get(col_type)

    if not expected_type_info:
        logger.add_message(f"Unknown column type {col_type} provided for validation.", 'error')
        return

    try:
        if col_type.startswith('Array('):
            converted_value = expected_type_info['convert'](col_val)
            
            if col_type == 'Array(VARCHAR(255))':
                logger.add_message(f"Value '{col_val}' was converted to {col_type} type.", 'info')
                return
            
            if str(col_val) != str(converted_value):
                logger.add_message(f"Value '{col_val}' was converted to {col_type} type.", 'warning')
        elif isinstance(col_val, expected_type_info['type']):
            return
        else:
            converted_value = expected_type_info['convert'](col_val)  # Attempt conversion
            logger.add_message(f"Value '{col_val}' was converted to {col_type} type.", 'warning')
    except (ValueError, TypeError) as e:
        logger.add_message(f"Error: Value '{col_val}' is not compatible with {col_type} type and cannot be converted. {str(e)}", 'error')
