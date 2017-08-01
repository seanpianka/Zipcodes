"""
zipcodes
~~~~~~~~

Lightweight U.S. zip-code validation package for Python (2 and 3).

:author: Sean Pianka
:github: @seanpianka

"""
import gzip
import json
import os
import re

__author__ = 'Sean Pianka'
__email__ = 'pianka@eml.cc'
__license__ = 'MIT'
__package__ = 'zipcodes'
__version__ = '1.0.0'

_digits = re.compile('[^\d\-]')

with gzip.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zips.json.gz'), 'rb') as f:
    zips = json.load(f)


def validated_zipcode(f):
    return lambda zipcode: f(_validate(zipcode))


@validated_zipcode
def matching(zipcode):
    '''
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
    '''
    return [z for z in zips if z['zip_code'] == zipcode]


@validated_zipcode
def is_valid(zipcode):
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
    return bool(matching(zipcode))


@validated_zipcode
def similar_to(partial_zipcode):
    '''
    Retrieve a list of zip-code dictionaries where the prefix matches the
    provided partial zip-code.

    Parameters
    ----------
    partial_zipcode : str
        The partial zip-code to match.

    Returns
    -------
    list of dict
        List of dictionaries containing "zip_code", "zip_code_type", "city",
        "state", "world_region", and "country" as keys. Example:

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
    '''
    return [z for z in zips if z['zip_code'].startswith(partial_zipcode)]


def _contains_nondigits(s):
    return bool(_digits.search(s))


def _validate(zipcode):
    if not isinstance(zipcode, str) or len(zipcode) == 0:
        raise TypeError('Zipcode must be a string.')
    if _contains_nondigits(zipcode) or not zipcode[0].isdigit() or not zipcode[-1].isdigit():
        raise TypeError('Zipcode may only contain digits and "-".')
    # More details on "ZIP+4" codes: https://smartystreets.com/articles/zip-4-code
    if '-' in zipcode and zipcode.count('-') == 1:  # zipcode of the form '06469-1145'
        zipcode = zipcode.split('-', 1)[0]          # keep '06469', discard '-1145'

    return zipcode
