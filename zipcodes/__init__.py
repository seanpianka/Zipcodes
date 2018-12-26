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
import warnings


__all__ = ["matching", "similar_to", "is_valid"]
__author__ = "Sean Pianka"
__email__ = "pianka@eml.cc"
__license__ = "MIT"
__package__ = "zipcodes"
__version__ = "1.0.5"


_digits = re.compile(r"[^\d\-]")
_zips_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zips.json.gz")
_valid_zipcode_length = 5

with gzip.open(_zips_json, "rb") as f:
    _zips = json.loads(f.read().decode("ascii"))


def _contains_nondigits(s):
    return bool(_digits.search(s))


def _clean_zipcode(f):
    def decorator(zipcode):
        if not zipcode or not isinstance(zipcode, str):
            raise TypeError("Invalid type, zipcode must be a string.")

        return f(_clean(zipcode, min(len(zipcode), _valid_zipcode_length)))

    return decorator


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


@_clean_zipcode
def matching(zipcode, zips=_zips):
    """ Retrieve zipcode dict for provided zipcode """
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
def similar_to(partial_zipcode, zips=_zips):
    """ List of zipcode dicts where zipcode prefix matches `partial_zipcode` """
    return [z for z in zips if z["zip_code"].startswith(partial_zipcode)]


def filter_by(zips=_zips, **kwargs):
    """ Use `kwargs` to select for desired attributes from list of zipcode dicts """
    return [z for z in zips if all([k in z and z[k] == v for k, v in kwargs.items()])]


def list_all(zips=_zips):
    """ Return a list containing all zip-code objects. """
    return zips
