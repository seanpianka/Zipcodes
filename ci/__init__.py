import json
from pprint import pprint

from ci._internal_utils import (
    parse_csv,
    split_by_comma,
    update_gps_coordinates,
    strip_unsupported_schema,
    perform_kv_transforms,
)


def main():
    SCHEMA = {
        "zip": {"public": "zip_code"},
        "type": {"public": "zip_code_type"},
        "decommissioned": {"public": "active", "transform": lambda v: not bool(int(v))},
        "primary_city": {"public": "city"},
        "acceptable_cities": {
            "public": "acceptable_cities",
            "transform": split_by_comma,
        },
        "unacceptable_cities": {
            "public": "unacceptable_cities",
            "transform": split_by_comma,
        },
        "state": {"public": "state"},
        "county": {"public": "county"},
        "timezone": {"public": "timezone"},
        "area_codes": {"public": "area_codes", "transform": split_by_comma},
        "world_region": {"public": "world_region"},
        "country": {"public": "country"},
        "latitude": {"public": "lat"},
        "longitude": {"public": "long"},
    }

    gps_zipcodes_filename = "ci/data/zip-codes-database-FREE.csv"
    base_zipcodes_filename = "ci/data/zip_code_database.csv"

    gps_data = parse_csv(gps_zipcodes_filename)
    base_data = parse_csv(base_zipcodes_filename)

    pprint("GPS Keys: {}".format(list(gps_data[0].keys())))
    pprint("Base Keys: {}".format(list(base_data[0].keys())))

    # Begin transforming base place data.
    base_data = update_gps_coordinates(gps_data, base_data)
    base_data = strip_unsupported_schema(base_data, SCHEMA)
    base_data = perform_kv_transforms(base_data, SCHEMA)

    print("Writing zipcode information for {} places".format(len(base_data)))

    with open("zips.json", "w") as f:
        json.dump(base_data, f)

    print("To zip for production, run:\n$ bzip2 zips.json")


if __name__ == "__main__":
    main()
