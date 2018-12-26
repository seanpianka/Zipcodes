"""
zipcodes
~~~~~~~~

No-SQLite U.S. zipcode validation Python package, ready for use in AWS Lambda

:author: Sean Pianka
:github: @seanpianka

"""
import gzip
import json
import os
import re


__all__ = ["matching", "similar_to", "is_valid"]
__author__ = "Sean Pianka"
__email__ = "pianka@eml.cc"
__license__ = "MIT"
__package__ = "zipcodes"
__version__ = "1.0.5"


_digits = re.compile(r"[^\d\-]")
_zips = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zips.json.gz")

with gzip.open(ZIP_CODES, "rb") as f:
    _zips = json.loads(f.read().decode("ascii"))


@_validated_zipcode
def matching(zipcode, zips=_zips):
    """
    Retrieve additional information about a zip-code such as the associated
    city and state. The provided zipcode can either be of the form '06469' or
    '06469-1154'. Zip-5-codes and Zip-9-codes are both supported.

    """
    return [z for z in zips if z["zip_code"] == zipcode]


@_validated_zipcode
def is_valid(zipcode):
    """
    Determine whether a given U.S. zip-code is valid. The provided zipcode
    can either be of the form '06469' or '06469-1154'. Zip-5-codes and
    Zip-9-codes are both supported.

    """
    return bool(matching(zipcode))


@_validated_zipcode
def similar_to(partial_zipcode, zips=_zips):
    """
    Retrieve a list of zip-code dictionaries where the prefix matches the
    provided partial zip-code.

    """
    return [z for z in zips if z["zip_code"].startswith(partial_zipcode)]


def filter_by(zips=_zips, **kwargs):
    """
    Filter through a list of zip-codes by providing keyword arguments and the
    values which should be filtered.

    """
    return [z for z in zips if all([k in z and z[k] == v for k, v in kwargs.items()])]


def list_all(zips=_zips):
    """ Return a list containing all zip-code objects. """
    return zips


def _contains_nondigits(s):
    return bool(_digits.search(s))


def _validate(zipcode):
    if not zipcode or not isinstance(zipcode, str):
        raise TypeError("Zipcode must be a string.")

    zipcode = zipcode.split("-")[0]  # Convert #####-#### to #####

    if len(zipcode) != 5:
        raise ValueError('Zipcode must be of format: "#####" or "#####-####"')

    if _contains_nondigits(zipcode):
        raise ValueError('Zipcode may only contain digits and "-".')

    return zipcode


def _validated_zipcode(f):
    return lambda zipcode, *args, **kwargs: f(_validate(zipcode), *args, **kwargs)
