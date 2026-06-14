"""Exercise the `zips=` override path of every query function.

The override path is implemented in the Rust binding (filtering the supplied
dicts in place); these tests assert it agrees with the database path on the
same subset.
"""
import zipcodes


def test_matching_with_zips_subset():
    subset = zipcodes.matching("06903")
    assert len(subset) == 1
    assert zipcodes.matching("06903", zips=subset) == subset
    assert zipcodes.matching("06903", zips=[]) == []
    assert zipcodes.matching("06903", zips=zipcodes.matching("06904")) == []


def test_matching_with_zips_returns_same_objects():
    subset = zipcodes.matching("06903")
    result = zipcodes.matching("06903", zips=subset)
    assert result[0] is subset[0]


def test_similar_to_with_zips_subset():
    windsor = zipcodes.filter_by(active=True, city="Windsor")
    assert len(zipcodes.similar_to("2", zips=windsor)) == 3
    assert zipcodes.similar_to("2", zips=zipcodes.filter_by(city="Old Saybrook")) == []


def test_contains_with_zips_subset():
    subset = zipcodes.similar_to("1018")
    matched = zipcodes.contains("0185", zips=subset)
    assert [z["zip_code"] for z in matched] == ["10185"]
    assert zipcodes.contains("99999", zips=subset) == []


def test_filter_by_bool_vs_int_on_zips_path():
    # The documented 2.x bool-vs-int distinction must hold on the override
    # path too: `active=1` matches nothing, `active=True` matches.
    subset = zipcodes.filter_by(city="Old Saybrook")
    assert len(subset) == 1
    assert zipcodes.filter_by(subset, active=True) == subset
    assert zipcodes.filter_by(subset, active=1) == []
    # Parity with the database path.
    assert zipcodes.filter_by(active=1) == []


def test_filter_by_missing_key_is_not_a_match():
    assert zipcodes.filter_by([{"city": "Old Saybrook"}], state="CT") == []


def test_filter_by_multiple_fields_on_zips_path():
    subset = zipcodes.filter_by_state("CT")
    saybrook = zipcodes.filter_by(subset, city="Old Saybrook", active=True)
    assert [z["zip_code"] for z in saybrook] == ["06475"]


def test_filter_by_coordinates_with_zips_subset():
    # Old Saybrook, CT — string lat/long as returned by the database path.
    subset = zipcodes.filter_by_state("CT")
    nearby = zipcodes.filter_by_coordinates(41.3015, -72.3879, 5, zips=subset)
    assert any(z["zip_code"] == "06475" for z in nearby)
    # Wrong hemisphere is nowhere near any CT zipcode.
    assert zipcodes.filter_by_coordinates(42.2529, 71.0023, 100, zips=subset) == []


def test_filter_by_coordinates_accepts_float_values():
    zips = [
        {"zip_code": "06475", "lat": 41.2913, "long": -72.385},
        {"zip_code": "90210", "lat": 34.0901, "long": -118.4065},
    ]
    nearby = zipcodes.filter_by_coordinates(41.3015, -72.3879, 5, zips=zips)
    assert [z["zip_code"] for z in nearby] == ["06475"]


def test_list_all_returns_zips_unchanged():
    zips = [{"zip_code": "06903"}]
    assert zipcodes.list_all(zips) is zips
