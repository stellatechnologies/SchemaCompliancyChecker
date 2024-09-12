import re


def regex_validator(val, regex):
    return re.match(regex, val) if val is not None else False


def nullable_validator(val, nullable):
    if isinstance(nullable, bool):
        return val is not None or nullable
    return val is not None or nullable.lower() in ['true', '1', 'yes']
