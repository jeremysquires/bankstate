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

def is_mon_dd_date(string):
    try:
        datetime.strptime(string, "%b %d")
        return True
    except ValueError:
        return False

def is_transaction_line(string):
    # starts with three letter month and day
    if not is_mon_dd_date(string[0:6]):
        return False
    return True
