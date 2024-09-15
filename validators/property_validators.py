# validators/property_validators.py

import re

def regex_validator(val, regex):
    if val is None:
        return False
    return re.match(regex, val) is not None

def nullable_validator(val, nullable):
    if isinstance(nullable, bool):
        return val is not None or nullable
    return val is not None or nullable.lower() in ['true', '1', 'yes']
