import csv
import time
import json
from pprint import pprint


def strip_unsupported_schema(base_data, schema):
    """Strip keys/columns if not in SCHEMA"""
    return [
        {key: value for key, value in place.items() if key in schema}
        for place in base_data
    ]
    

def perform_kv_transforms(base_data, schema):
    """Perform any necessary transforming of either the key or value.

    :param base_data: original list of dicts of places
    :param schema: schema
    :return: list of dicts of places with keys moved or values modified

    [{'acceptable_cities': [],
     'active': True,
     'area_codes': ['631'],
     'city': 'Bohemia',
     'country': 'US',
     'county': 'Suffolk County',
     'lat': '40.7702',
     'long': '-73.1250',
     'state': 'NY',
     'timezone': 'America/New_York',
     'unacceptable_cities': [],
     'world_region': 'NA',
     'zip_code': '11716',
     'zip_code_type': 'STANDARD'},
     ...]

    """
    return [
        {
            schema[key]["public"]: schema[key]["transform"](value)
            if "transform" in schema[key]
            else value
            for key, value in place.items()
            if all((isinstance(schema[key], dict),))
        }
        for place in base_data
    ]


def parse_csv(filename):
    """Convert CSV file to list of dictionaries.

    Source: https://stackoverflow.com/a/21572244/4562156

    :param filename: filename containing CSV data (relative to project root)
    :return: list of dictionaries representing each row with CSV schema as keys
    """
    with open(filename) as f:
        return [
            {k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)
        ]

def split_by_comma(s):
    """Split a string by comma, trim each resultant string element, and remove falsy-values.

    :param s: str to split by comma
    :return: list of provided string split by comma
    """
    return [i.strip() for i in s.split(",") if i]


def main():
    """This script loads the raw zipcode data from scripts/data and combines
    them both into the final dataset that is used by the library.

    We define a dict that holds the "schema" the JSON returned by library
    (query) calls. The dict's keys are the field name from the transformed
    dataset, and the value is a dict that contains the "public" field name in
    this library's API, along with an optional pre-processing function for the
    transformation.

    """
    # This is the key layout of the unitedstatezipcodes' dataset mapped to this
    # library's public API.
    #
    # dataset_field_name to resultant_zips_json_field_name
    SCHEMA = {
        "DELIVERY ZIPCODE": {"public": "zip_code"},
        "PHYSICAL STATE": {"public": "state"},
        "PHYSICAL ZIP": {"public": "other_zip"}
    }

    # Original free data sample from unitedstateszipcodes
    base_zipcodes_filename = "scripts/data/ZIP_Locale_Detail.csv"

    base_data = parse_csv(base_zipcodes_filename)

    pprint(f"Base Keys: {list(base_data[0].keys())}, Len: {len(base_data)}")

    # Begin transforming base place data.
    base_data = strip_unsupported_schema(base_data, SCHEMA)
    base_data = perform_kv_transforms(base_data, SCHEMA)
    print(base_data)
    print(list(filter(lambda i: i["zip_code"] == "11428", base_data)))

    pprint(f"Updated Base Base Keys: {list(base_data[0].keys())}, Len: {len(base_data)}")

    with open("zips.json", "w") as f:
        json.dump(base_data, f)

    print(len(base_data))

    print("To zip for production, run:\n$ bzip2 zips.json")


main()
