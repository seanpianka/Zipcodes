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
__all__ = ['matching', 'similar_to', 'is_valid']

_digits = re.compile('[^\d\-]')

with gzip.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zips.json.gz'), 'rb') as f:
    _zips = json.load(f)


def validated_zipcode(f):
    return lambda zipcode, *args, **kwargs: f(_validate(zipcode), *args, **kwargs)


@validated_zipcode
def matching(zipcode, zips=_zips):
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

        >>> zipcodes.matching('77429')
        [{'zip_code': '77429',
          'zip_code_type': 'STANDARD',
          'city': 'CYPRESS',
          'state': 'TX',
          'lat': 29.96,
          'long': -95.69,
          'world_region': 'NA',
          'country': 'US',
          'active': True}]

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

    >>> zipcodes.is_valid('77429')
    True


    Raises
    ------
    TypeError
        When the zip-code is not a string or contains characters other than
        digits and "-".
    """
    return bool(matching(zipcode))


@validated_zipcode
def similar_to(partial_zipcode, zips=_zips):
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

        >>> zipcodes.similar_to('0643')
        [{'active': True,
          'city': 'GUILFORD',
          'country': 'US',
          'lat': 41.28,
          'long': -72.67,
          'state': 'CT',
          'world_region': 'NA',
          'zip_code': '06437',
          'zip_code_type': 'STANDARD'},
         {'active': True,
          'city': 'HADDAM',
          'country': 'US',
          'lat': 41.45,
          'long': -72.5,
          'state': 'CT',
          'world_region': 'NA',
          'zip_code': '06438',
          'zip_code_type': 'STANDARD'},
         {'active': True,
          'city': 'HADLYME',
          'country': 'US',
          'lat': 41.4,
          'long': -72.34,
          'state': 'CT',
          'world_region': 'NA',
          'zip_code': '06439',
          'zip_code_type': 'PO BOX'}]

    Raises
    ------
    TypeError
        When the zip-code is not a string or contains characters other than
        digits and "-".
    '''
    return [z for z in zips if z['zip_code'].startswith(partial_zipcode)]


def filter_by(zips, **kwargs):
    """
    Filter through a list of zip-codes by providing keyword arguments and the
    values which should be filtered.

    Parameters
    ----------
    zips : list of dict
        A list containing each dictionary object with which to filter through.
    kwargs : dict
        A dictionary containing pairs where the key is the attribute to filter
        by, and its corresponding value is the value to filter for the
        aforementioned key.

    Returns
    -------
    list of dict
        A list containing each dictionary object which was filtered.

    >>> pprint(zipcodes.similar_to('2', zips=zipcodes.filter_by(zipcodes.list_all(), active=True, city='WINDSOR')))
    [{'active': True,
      'city': 'WINDSOR',
      'country': 'US',
      'lat': 33.48,
      'long': -81.51,
      'state': 'SC',
      'world_region': 'NA',
      'zip_code': '29856',
      'zip_code_type': 'STANDARD'},
     {'active': True,
      'city': 'WINDSOR',
      'country': 'US',
      'lat': 36.8,
      'long': -76.73,
      'state': 'VA',
      'world_region': 'NA',
      'zip_code': '23487',
      'zip_code_type': 'STANDARD'},
     {'active': True,
      'city': 'WINDSOR',
      'country': 'US',
      'lat': 36.0,
      'long': -76.94,
      'state': 'NC',
      'world_region': 'NA',
      'zip_code': '27983',
      'zip_code_type': 'STANDARD'}]


    """
    results = zips
    for k, v in kwargs.items():
        results = [r for r in results if r.get(k) == v]
    return results


def list_all(zips=_zips):
    """
    Return a list containing all zip-code objects.

    Returns
    -------
    list of dict
        A list containing all zip-code objects.

    >>> zipcodes.filter_by(zipcodes.list_all(), active=True, state='CT')
    ... # all zip-codes for the state of Connecticut.

    """
    return zips


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
