import os
import sys
import unittest

# append module root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import zipcodes


class TestZipcodes(unittest.TestCase):
    def test_is_real(self):
        self.assertTrue(zipcodes.is_real("06469"))
        self.assertFalse(zipcodes.is_real("06463"))

        with self.assertRaises(TypeError):
            zipcodes.is_real(None)

    def test_matching(self):
        self.assertEqual(
            zipcodes.similar_to("10001"),
            [
                {
                    "zip_code": "10001",
                    "zip_code_type": "STANDARD",
                    "city": "NEW YORK",
                    "state": "NY",
                    "lat": 40.71,
                    "long": -73.99,
                    "world_region": "NA",
                    "country": "US",
                    "active": True,
                }
            ],
        )

    def test_similar_to(self):
        self.assertEqual(
            zipcodes.similar_to("0643"),
            [
                {
                    "zip_code": "06437",
                    "zip_code_type": "STANDARD",
                    "city": "GUILFORD",
                    "state": "CT",
                    "lat": 41.28,
                    "long": -72.67,
                    "world_region": "NA",
                    "country": "US",
                    "active": True,
                },
                {
                    "zip_code": "06438",
                    "zip_code_type": "STANDARD",
                    "city": "HADDAM",
                    "state": "CT",
                    "lat": 41.45,
                    "long": -72.5,
                    "world_region": "NA",
                    "country": "US",
                    "active": True,
                },
                {
                    "zip_code": "06439",
                    "zip_code_type": "PO BOX",
                    "city": "HADLYME",
                    "state": "CT",
                    "lat": 41.4,
                    "long": -72.34,
                    "world_region": "NA",
                    "country": "US",
                    "active": True,
                },
            ],
        )

    def test_filter_by(self):
        self.assertEqual(
            zipcodes.filter_by(city="WINDSOR", state="CT"),
            [
                {
                    "zip_code": "06006",
                    "zip_code_type": "UNIQUE",
                    "city": "WINDSOR",
                    "state": "CT",
                    "lat": 41.85,
                    "long": -72.65,
                    "world_region": "NA",
                    "country": "US",
                    "active": True,
                },
                {
                    "zip_code": "06095",
                    "zip_code_type": "STANDARD",
                    "city": "WINDSOR",
                    "state": "CT",
                    "lat": 41.85,
                    "long": -72.65,
                    "world_region": "NA",
                    "country": "US",
                    "active": True,
                },
            ],
        )

    def test_list_all(self):
        self.assertEqual(zipcodes.list_all(), zipcodes._zips)

    def test__clean(self):
        # bad length
        with self.assertRaises(ValueError):
            zipcodes._clean("000000")

        # bad characters
        with self.assertRaises(ValueError):
            zipcodes._clean("0000a")

        # valid_zipcode_length parameter
        self.assertEqual(zipcodes._clean("0646", 4), "0646")

        # default behavior
        self.assertEqual(zipcodes._clean("06469"), "06469")

    def test__contains_nondigits(self):
        # digits and "-" are acceptable
        self.assertFalse(zipcodes._contains_nondigits("12345"))
        self.assertFalse(zipcodes._contains_nondigits("1234-"))

        # anything else is not
        self.assertTrue(zipcodes._contains_nondigits("1234a"))


if __name__ == "__main__":
    unittest.main()
