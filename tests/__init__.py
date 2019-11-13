import os
import sys
import unittest

# append module root directory to sys.path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import zipcodes
from tests.logger import CustomLogger

logger = CustomLogger(__name__)


class TestZipcodes(unittest.TestCase):
    pass


def callable_raise_exc(function, exception, *args, **kwargs):
    try:
        function(*args, **kwargs)
        return False
    except Exception as e:
        logger.debug(e)
        logger.debug(exception)
        return isinstance(e, exception)


def generate_unittest(name, assertion_callable, predicate):
    """

    :param tracking_index: index of callable within predicate list for each stage
    :param assertion_callable: callable which generates the assertion statement using test context
    :param predicate: arguments to provide the assertion
    :return:
    """

    def test(self):
        assertion = assertion_callable(self)

        logger.debug(
            "Name: {}\nPredicate: {}\nAssertion: {}".format(
                name, predicate, assertion_callable
            )
        )

        if isinstance(predicate, (list, tuple)):
            assertion(*[func() for func in predicate])
        elif callable(predicate):
            assertion(predicate())
        else:
            raise ValueError("Predicate must be a lambda or a vector of lambdas\n")

    return test


def generate_unittests(unittests_schema):
    """ The return from invoking the predicates should match the assertion. """
    # Parser
    for idx_stage, stage in enumerate(unittests_schema):
        for idx_predicate, predicate in enumerate(stage["predicates"]):
            test_name = "test_{}_idx_{}".format(stage["name"], idx_predicate)
            setattr(
                TestZipcodes,
                test_name,
                generate_unittest(test_name, stage["assertion"], predicate),
            )


def main():
    # name of this stage, typically a name to reference the assertion
    # assertion: lambda which returns unittest callable with self's (testcase's) context
    # predicates: lambda or sequence of lambdas to call and pass to the assertion
    unittests_schema = [
        {
            "name": "true",
            "assertion": lambda self: self.assertTrue,
            "predicates": [
                lambda: zipcodes.is_real("06905"),
                lambda: zipcodes._contains_nondigits("1234a"),
                # bad length
                lambda: callable_raise_exc(
                    lambda: zipcodes._clean("000000"), ValueError
                ),
                # bad characters
                lambda: callable_raise_exc(
                    lambda: zipcodes._clean("0000a"), ValueError
                ),
                # ensure zips argument works
                lambda: len(
                    zipcodes.similar_to(
                        "2", zips=zipcodes.filter_by(active=True, city="Windsor")
                    )
                )
                == 3,
            ],
        },
        {
            "name": "false",
            "assertion": lambda self: self.assertFalse,
            "predicates": [
                lambda: zipcodes.is_real("91239"),
                # digits and "-" are acceptable
                lambda: zipcodes._contains_nondigits("12345"),
                lambda: zipcodes._contains_nondigits("1234-"),
            ],
        },
        {
            "name": "equal",
            "assertion": lambda self: self.assertEqual,
            "predicates": [
                # valid_zipcode_length parameter
                (lambda: zipcodes._clean("0646", 4), lambda: "0646"),
                # default behavior
                (lambda: zipcodes._clean("06469"), lambda: "06469"),
                (lambda: zipcodes.list_all(), lambda: zipcodes._zips),
                (
                    lambda: zipcodes.filter_by(city="Old Saybrook"),
                    lambda: [
                        {
                            "zip_code": "06475",
                            "zip_code_type": "STANDARD",
                            "active": True,
                            "city": "Old Saybrook",
                            "acceptable_cities": [],
                            "unacceptable_cities": ["Fenwick"],
                            "state": "CT",
                            "county": "Middlesex County",
                            "timezone": "America/New_York",
                            "area_codes": ["860"],
                            "world_region": "NA",
                            "country": "US",
                            "lat": "41.3015",
                            "long": "-72.3879",
                        }
                    ],
                ),
                (
                    lambda: zipcodes.similar_to("1018"),
                    lambda: [
                        {
                            "acceptable_cities": [],
                            "active": False,
                            "area_codes": ["212"],
                            "city": "New York",
                            "country": "US",
                            "county": "New York County",
                            "lat": "40.71",
                            "long": "-74",
                            "state": "NY",
                            "timezone": "America/New_York",
                            "unacceptable_cities": ["J C Penney"],
                            "world_region": "NA",
                            "zip_code": "10184",
                            "zip_code_type": "UNIQUE",
                        },
                        {
                            "acceptable_cities": [],
                            "active": True,
                            "area_codes": ["212"],
                            "city": "New York",
                            "country": "US",
                            "county": "New York County",
                            "lat": "40.7143",
                            "long": "-74.0067",
                            "state": "NY",
                            "timezone": "America/New_York",
                            "unacceptable_cities": [],
                            "world_region": "NA",
                            "zip_code": "10185",
                            "zip_code_type": "PO BOX",
                        },
                    ],
                ),
                (
                    lambda: zipcodes.similar_to("1005"),
                    lambda: [
                        {
                            "zip_code": "10055",
                            "zip_code_type": "STANDARD",
                            "active": True,
                            "city": "New York",
                            "acceptable_cities": [],
                            "unacceptable_cities": ["Manhattan"],
                            "state": "NY",
                            "county": "New York County",
                            "timezone": "America/New_York",
                            "area_codes": ["212"],
                            "world_region": "NA",
                            "country": "US",
                            "lat": "40.7579",
                            "long": "-73.9743",
                        }
                    ],
                ),
                (
                    lambda: zipcodes.similar_to("10001"),
                    lambda: [
                        {
                            "zip_code": "10001",
                            "zip_code_type": "STANDARD",
                            "active": True,
                            "city": "New York",
                            "acceptable_cities": [],
                            "unacceptable_cities": [
                                "Empire State",
                                "G P O",
                                "Greeley Square",
                                "Macys Finance",
                                "Manhattan",
                            ],
                            "state": "NY",
                            "county": "New York County",
                            "timezone": "America/New_York",
                            "area_codes": ["718", "917", "347", "646"],
                            "world_region": "NA",
                            "country": "US",
                            "lat": "40.7508",
                            "long": "-73.9961",
                        }
                    ],
                ),
            ],
        },
    ]

    generate_unittests(unittests_schema)
    logger.info("Zipcodes version: {}".format(zipcodes.__version__))
    unittest.main()


if __name__ == "__main__":
    main()
