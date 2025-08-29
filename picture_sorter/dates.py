"""
File for parsing dates.
"""

from collections.abc import Callable
import datetime
import logging
import re


class NoDateFound(Exception):
    """
    Exception raised when no valid date can be extracted from a string.
    """


def parse_yyyymmdd(string: str) -> datetime.datetime:
    """
    Parse a date in the format YYYYMMDD from a string.

    This function looks for a sequence of 8 digits that represents a valid
    date.
    If the string contains more than one possible match or no match at all, an
    exception is raised.

    :param string: Input string potentially containing a date.
    :return: A datetime object representing the parsed date.
    :raises NoDateFound: If no valid date is found or the date is invalid.
    """
    pattern = r"(?=(\d{4})(\d{2})(\d{2}))"
    matches = re.findall(pattern, string)
    if len(matches) != 1:
        raise NoDateFound(f"Invalid number of dates found in '{string}'.")

    year, month, day = map(int, matches[0])
    try:
        return datetime.datetime(year, month, day)
    except ValueError as e:
        raise NoDateFound(
            f"The date {year}-{month}-{day} is not valid."
        ) from e


def parse_date(string: str) -> datetime.datetime:
    """
    Try to parse a date from a string using different parsing strategies.

    :param string: Input string containing a potential date.
    :return: A datetime object representing the parsed date.
    :raises NoDateFound: If no parser can extract a valid date.
    """
    parsers: list[Callable[[str], datetime.datetime]] = [parse_yyyymmdd]

    logging.debug("Parsing '%s'.", string)
    for parser in parsers:
        logging.debug("Parser: %s.", parser.__name__)
        try:
            date = parser(string)
            logging.debug("Date found '%s'.", date)
            return date
        except NoDateFound:
            logging.debug("Date not found.")
            continue

    logging.debug("None parser worked.")
    raise NoDateFound(f'No date pattern found in "{string}".')
