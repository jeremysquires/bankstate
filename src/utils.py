from datetime import datetime
from typing import List
from dateutil.parser import parse

MAX_FIELD_LENGTH = 128


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True
    except ValueError:
        return False


def is_format_date(string, format_string):
    try:
        datetime.strptime(string, format_string)
        return True
    except ValueError:
        return False


def is_two_part_date(string):
    return (
        is_mon_dot_dd_date(string) or is_mon_dd_date(string) or is_dd_mon_date(string)
    )


def switch_two_part_date(string):
    date_part = string.split(" ")
    return f"{date_part[1]} {date_part[0]}"


# NOTE: this does not check for longer strings
def normalize_mon_dd(string):
    if len(string) < 4:
        return ""
    return string[0] + string[1:3].lower() + string[3:]


# NOTE: this does not check for longer strings
def normalize_dd_mon(string):
    if len(string) < 2:
        return string
    return string[0:-2] + string[-2:].lower()


def is_mon_dd_date(string):
    return is_format_date(normalize_mon_dd(string), "%b %d")


def is_dd_mon_date(string):
    return is_format_date(normalize_dd_mon(string), "%d %b")


def is_mon_dot_dd_date(string):
    return is_format_date(normalize_mon_dd(string), "%b. %d")


def normalize_to_mon_dd_yyyy(string):
    if len(string) < 4:
        return ""
    string = string.replace(".", "")
    return string[0] + string[1:3].lower() + string[3:]


def normalize_to_dd_mon(string):
    dd_mon = None
    string = string.replace(".", "")
    if is_mon_dd_date(string):
        dd_mon = switch_two_part_date(normalize_mon_dd(string))
    else:
        dd_mon = normalize_dd_mon(string)
    return dd_mon


def is_transaction_line(string):
    # starts with three letter month and day
    if not is_mon_dd_date(string[0:6]):
        return False
    return True


def is_float(string):
    try:
        float(string)
        return bool("." in string)
    except ValueError:
        return False


def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def is_currency(string):
    # remove thousands separators and $ from currency, then check float
    return is_float(string.replace(",", "").replace("$", ""))


def currency_to_float(string):
    # remove thousands separators and $ from currency
    # return None if input is not currency
    if not is_currency(string):
        return None
    return string.replace(",", "").replace("$", "")


def trim_parts(parts: List[str]) -> List[str]:
    return [
        part if len(part) < MAX_FIELD_LENGTH else " ".join(part.split(" ")[-2:])
        for part in parts
    ]


def normalize_date_range(string):
    # variants on Mon dd, yyyy TO/- Mon dd, yyyy
    from_date, to_date = tuple(
        string.split("TO")
        if "TO" in string
        else (string.split("-") if "-" in string else [None, None])
    )
    if not from_date or not to_date:
        return None, None
    from_date = normalize_to_mon_dd_yyyy(from_date.strip())
    to_date = normalize_to_mon_dd_yyyy(to_date.strip())
    # fix the missing yyyy in some date ranges
    if is_mon_dd_date(from_date) and is_format_date(to_date, "%b %d, %Y"):
        from_date = from_date + f", {to_date[-4:]}"
    if is_format_date(from_date, "%b %d, %Y") and is_format_date(to_date, "%b %d, %Y"):
        return from_date, to_date
    return None, None
