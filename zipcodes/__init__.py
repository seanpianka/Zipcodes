"""
zipcodes
~~~~~~~~

Lightweight U.S. zip-code validation package for Python (2 and 3).

:author: Sean Pianka
:github: @seanpianka

"""
import json
import re
import os

_digits = re.compile('[^\d\-]')

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zips.json')) as f:
    zips = json.load(f)


def validated_zipcode(f):
    return lambda zipcode: f(_validate(zipcode))


@validated_zipcode
def get_zipcode(zipcode):
    """
    Retrieve additional information about a zip-code such as the associated
    city and state. The provided zipcode can either be of the form '06469' or
    '06469-1154'. Zip-5-codes and Zip-9-codes are both supported.

    Parameters
    ----------
    zipcode : str
        The zip-code to find more information about.

    Returns
    -------
    dict
        Dictionary containing "zip_code", "zip_code_type", "city", "state",
        "world_region", and "country" as keys. Example:

        >>> {"zip_code": "00705",
             "zip_code_type": "STANDARD",
             "city": "AIBONITO",
             "state": "PR",
             "world_region": "NA",
             "country": "US"}

    Raises
    ------
    TypeError
        When the zip-code is not a string or contains characters other than
        digits and "-".
    """
    if not any(z['zip_code'] == zipcode for z in zips):
        return None
    return [z for z in zips if z['zip_code'] == zipcode]


@validated_zipcode
def is_valid_zipcode(zipcode):
    """
    Determine whether a given U.S. zip-code is valid. The provided zipcode
    can either be of the form '06469' or '06469-1154'. Zip-5-codes and
    Zip-9-codes are both supported.

    Parameters
    ----------
    zipcode : str
        The zip-code to test for validity.

    Returns
    -------
    bool
        Whether the provided zip-code is valid.

    Raises
    ------
    TypeError
        When the zip-code is not a string or contains characters other than
        digits and "-".
    """
    return bool(get_zipcode(zipcode))


def _contains_nondigits(s):
    return bool(_digits.search(s))


def _validate(zipcode):
    if not isinstance(zipcode, str) or len(zipcode) == 0:
        raise TypeError('Zipcode must be a string.')
    if _contains_nondigits(zipcode) or not zipcode[0].isdigit() or not zipcode[-1].isdigit():
        raise TypeError('Zipcode may only contain digits and "-".')
    # More details on "ZIP+4" codes: https://smartystreets.com/articles/zip-4-code
    if '-' in zipcode and zipcode.count('-') == 1: # zipcode of the form '06469-1145'
        zipcode = zipcode.split('-', 1)[0]         # keep '06469', discard '-1145'

    return zipcode
