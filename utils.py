from datetime import datetime
from dateutil.parser import parse


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


def is_format_date(string, format):
    try:
        datetime.strptime(string, format)
        return True
    except ValueError:
        return False


def is_mon_dd_date(string):
    return is_format_date(string, "%b %d")


def is_dd_mon_date(string):
    return is_format_date(string, "%d %b")


def is_mon_dot_dd_date(string):
    return is_format_date(string, "%b. %d")


def is_transaction_line(string):
    # starts with three letter month and day
    if not is_mon_dd_date(string[0:6]):
        return False
    return True


def is_float(string):
    try:
        float(string)
        if "." in string:
            return True
        else:
            return False
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
