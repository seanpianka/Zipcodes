"""
zipcodes
~~~~~~~~

No-SQLite U.S. zipcode validation Python package, ready for use in AWS Lambda

:author: Sean Pianka
:github: @seanpianka

All queries — full-database scans and ``zips=`` chaining lists alike — run in
the compiled Rust extension (``zipcodes._zipcodes``); this module preserves
the exact 1.x behavior for argument validation and exceptions.
"""
import re
import warnings

from zipcodes import _zipcodes

__author__ = "Sean Pianka"
__email__ = "pianka@eml.cc"
__license__ = "MIT"
__version__ = _zipcodes.__version__

_digits = re.compile(r"[^\d\-]")
_valid_zipcode_length = 5

_zips_cache = None


def _load_zips():
    global _zips_cache
    if _zips_cache is None:
        _zips_cache = _zipcodes.list_all()
    return _zips_cache


def __getattr__(name):
    # `_zips` was a module-level list in 1.x; keep it importable, but
    # materialize the 42k dicts lazily instead of at import time.
    if name == "_zips":
        return _load_zips()
    raise AttributeError("module {!r} has no attribute {!r}".format(__name__, name))


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
    """Retrieve zipcode dict for provided zipcode"""
    return _zipcodes.matching(zipcode, zips=zips)


@_clean_zipcode
def is_valid(zipcode):
    warnings.warn("is_valid is deprecated; use is_real", DeprecationWarning, stacklevel=2)
    return is_real(zipcode)


@_clean_zipcode
def is_real(zipcode):
    """Determine whether a given zip or zip+4 zipcode is real."""
    return _zipcodes.is_real(zipcode)


@_clean_zipcode
def similar_to(partial_zipcode, zips=None):
    """List of zipcode dicts where zipcode prefix matches `partial_zipcode`"""
    return _zipcodes.similar_to(partial_zipcode, zips=zips)


@_clean_zipcode
def contains(partial_zipcode, zips=None):
    """List of zipcode dicts where zipcode contains `partial_zipcode` fragment"""
    return _zipcodes.contains(partial_zipcode, zips=zips)


def filter_by_state(state, zips=None):
    return filter_by(zips, state=state)


def filter_by_city(city, zips=None):
    return filter_by(zips, city=city)


def filter_by_county(county, zips=None):
    return filter_by(zips, county=county)


def filter_by_timezone(timezone, zips=None):
    return filter_by(zips, timezone=timezone)


def filter_by_zip_code_type(zip_code_type, zips=None):
    return filter_by(zips, zip_code_type=zip_code_type)


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in miles between two points
    on the earth (specified in decimal degrees)
    """
    return _zipcodes.haversine(lon1, lat1, lon2, lat2)


def filter_by_coordinates(lat, long, radius_in_miles=10, zips=None):
    """List of zipcode dicts within `radius_in_miles` of (`lat`, `long`)."""
    return _zipcodes.filter_by_coordinates(lat, long, radius_in_miles, zips=zips)


def filter_by(zips=None, **filters):
    """Use `kwargs` to select for desired attributes from list of zipcode dicts"""
    return _zipcodes.filter_by(zips, **filters)


def list_all(zips=None):
    """Return a list containing all zip-code objects."""
    if zips is None:
        return _load_zips()
    return zips


def _contains_nondigits(s):
    return bool(_digits.search(s))


def _clean(zipcode, valid_length=_valid_zipcode_length):
    """Assumes zipcode is of type `str`"""
    zipcode = zipcode.split("-")[0]  # Convert #####-#### to #####

    if len(zipcode) != valid_length:
        raise ValueError(
            'Invalid format, zipcode must be of the format: "#####" or "#####-####"'
        )

    if _contains_nondigits(zipcode):
        raise ValueError('Invalid characters, zipcode may only contain digits and "-".')

    return zipcode
