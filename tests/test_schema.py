"""Pin the dict builder's output to the crate's canonical field order.

`zipcodes._zipcodes.FIELD_ORDER` is exposed straight from `zipcodes::FIELD_ORDER`,
which the Rust `field_order_matches_struct` test pins to the struct. Asserting the
returned dict's keys equal it closes the drift loop on the Python side.
"""
import zipcodes
from zipcodes import _zipcodes


def test_dict_key_order_matches_field_order():
    record = zipcodes.matching("06903")[0]
    assert list(record.keys()) == list(_zipcodes.FIELD_ORDER)


def test_value_types():
    record = zipcodes.matching("06903")[0]
    assert isinstance(record["active"], bool)
    assert isinstance(record["area_codes"], list)
