"""Validation behavior for the unified Rust-core rules.

Every assertion goes through the public ``zipcodes`` functions; the rules
themselves live in the Rust core (``clean_zipcode`` / ``clean_prefix``) and the
binding translates ``zipcodes::Error`` into the 1.x ``ValueError`` messages. The
``TypeError`` for non-str input stays in the Python shim (``_require_str``).

Realness booleans are anchored to zipcodes whose existence is fixed by the core
crate's own tests ("06903" real; "06463"/"91239" fake), so they do not drift
with monthly dataset updates.
"""
import pytest

import zipcodes

_TYPE_MESSAGE = "Invalid type, zipcode must be a string."


# --- breaking change: input shorter than five chars now raises -------------
@pytest.mark.parametrize("func", [zipcodes.is_real, zipcodes.matching])
def test_short_input_raises_invalid_format(func):
    with pytest.raises(ValueError, match="Invalid format"):
        func("123")


@pytest.mark.parametrize("func", [zipcodes.is_real, zipcodes.matching])
def test_non_digit_raises_invalid_characters(func):
    with pytest.raises(ValueError, match="Invalid characters"):
        func("1234a")


# --- relaxations: whitespace and space-separated +4 are accepted -----------
def test_surrounding_whitespace_is_trimmed():
    assert zipcodes.is_real("  06903  ") is True


def test_space_separated_plus_four_is_accepted():
    # "##### ####" normalizes to its first five digits, like "#####-####".
    assert zipcodes.is_real("06903 1234") is True
    assert zipcodes.is_real("06463 1234") is False
    assert zipcodes.matching("06903 1234")[0]["zip_code"] == "06903"


# --- type guard stays in Python with the exact 1.x message -----------------
@pytest.mark.parametrize("bad", [12345, "", None])
def test_non_str_input_raises_typeerror(bad):
    with pytest.raises(TypeError) as excinfo:
        zipcodes.matching(bad)
    assert str(excinfo.value) == _TYPE_MESSAGE


# --- prefixes/fragments share one rule via clean_prefix --------------------
def test_prefix_with_non_digit_raises():
    with pytest.raises(ValueError, match="Invalid characters"):
        zipcodes.similar_to("10a")


def test_prefix_too_long_raises():
    with pytest.raises(ValueError, match="Invalid format"):
        zipcodes.similar_to("123456")


# --- the zips= override path validates too ---------------------------------
def test_override_path_validates_zipcode():
    with pytest.raises(ValueError, match="Invalid format"):
        zipcodes.matching("123", zips=[])


# --- is_valid is deprecated but still answers is_real ----------------------
def test_is_valid_warns_and_delegates():
    with pytest.warns(DeprecationWarning):
        assert zipcodes.is_valid("06903") is True


def test_private_validation_helpers_are_gone():
    for name in ("_clean", "_contains_nondigits", "_digits", "_valid_zipcode_length"):
        assert not hasattr(zipcodes, name), name
