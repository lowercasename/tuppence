from datetime import datetime


def validate_month(month):
    """Returns the month as an integer, or the current month if invalid"""
    try:
        if month is None:
            raise ValueError
        month = int(month)
        if month < 1 or month > 12:
            raise ValueError
    except ValueError:
        now = datetime.now()
        month = now.month
    return month

def validate_year(year):
    """Returns the year as an integer, or the current year if invalid"""
    try:
        if year is None:
            raise ValueError
        year = int(year)
        if year < 1:
            raise ValueError
    except ValueError:
        now = datetime.now()
        year = now.year
    return year