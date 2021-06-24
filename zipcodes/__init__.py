"""
zipcodes
~~~~~~~~

No-SQLite U.S. zipcode validation Python package, ready for use in AWS Lambda

:author: Sean Pianka
:github: @seanpianka

"""
import bz2
import json
import os
import re
import sys
import warnings

if sys.version_info >= (3, 0):
    bz2_open = bz2.open
else:
    bz2_open = bz2.BZ2File

__author__ = "Sean Pianka"
__email__ = "pianka@eml.cc"
__license__ = "MIT"
__package__ = "zipcodes"
__version__ = "1.1.3"

_digits = re.compile(r"[^\d\-]")
_valid_zipcode_length = 5


def _resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder nad stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


_zips_json = _resource_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "zips.json.bz2"))
with bz2_open(_zips_json, "rb") as f:
    _zips = json.loads(f.read().decode("ascii"))


def _clean_zipcode(fn):
    def decorator(zipcode, *args, **kwargs):
        if not zipcode or not isinstance(zipcode, str):
            raise TypeError("Invalid type, zipcode must be a string.")

        return fn(
            _clean(zipcode, min(len(zipcode), _valid_zipcode_length)), *args, **kwargs
        )

    return decorator


@_clean_zipcode
def matching(zipcode, zips=None):
    """ Retrieve zipcode dict for provided zipcode """
    if zips is None:
        zips = _zips
    return [z for z in zips if z["zip_code"] == zipcode]


@_clean_zipcode
def is_valid(zipcode):
    warnings.warn("is_valid is deprecated; use is_real", warnings.DeprecationWarning)
    return is_real(zipcode)


@_clean_zipcode
def is_real(zipcode):
    """ Determine whether a given zip or zip+4 zipcode is real. """
    return bool(matching(zipcode))


@_clean_zipcode
def similar_to(partial_zipcode, zips=None):
    """ List of zipcode dicts where zipcode prefix matches `partial_zipcode` """
    if zips is None:
        zips = _zips
    return [z for z in zips if z["zip_code"].startswith(partial_zipcode)]


def filter_by(zips=None, **filters):
    """ Use `kwargs` to select for desired attributes from list of zipcode dicts """
    if zips is None:
        zips = _zips

    return [
        zip
        for zip in zips
        if all([key in zip and zip[key] == value for key, value in filters.items()])
    ]


def list_all(zips=None):
    """ Return a list containing all zip-code objects. """
    if zips is None:
        zips = _zips
    return zips


def _contains_nondigits(s):
    return bool(_digits.search(s))


def _clean(zipcode, valid_length=_valid_zipcode_length):
    """ Assumes zipcode is of type `str` """
    zipcode = zipcode.split("-")[0]  # Convert #####-#### to #####

    if len(zipcode) != valid_length:
        raise ValueError(
            'Invalid format, zipcode must be of the format: "#####" or "#####-####"'
        )

    if _contains_nondigits(zipcode):
        raise ValueError('Invalid characters, zipcode may only contain digits and "-".')

    return zipcode
