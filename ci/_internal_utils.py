import csv
import time


def update_gps_coordinates(gps_data, base_data):
    info_place_by_zipcode = _index_list_of_dict_by_key(base_data, key="zip")

    start = time.time()
    for place in gps_data:
        try:
            info_place = info_place_by_zipcode[place["ZipCode"]]
        except KeyError:
            continue

        info_place_idx = info_place["index"]
        # {'index': 1, 'id': '2345', 'name': 'Tom'}

        base_data[info_place_idx]["latitude"] = place["Latitude"]
        base_data[info_place_idx]["longitude"] = place["Longitude"]

    end = time.time()
    print(
        "Updated GPS from GPS CSV in {} seconds.".format(end - start)
    )  # Updated in 0.02237415313720703 seconds.

    return base_data


def strip_unsupported_schema(base_data, schema):
    """ Strip keys/columns if not in SCHEMA """
    return [
        {key: value for key, value in place.items() if key in schema}
        for place in base_data
    ]


def perform_kv_transforms(base_data, schema):
    """ Perform any necessary transforming of either the key or value.

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
    """ Convert CSV file to list of dictionaries.

    Source: https://stackoverflow.com/a/21572244/4562156

    :param filename: filename containing CSV data (relative to project root)
    :return: list of dictionaries representing each row with CSV schema as keys
    """
    with open(filename) as f:
        return [
            {k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)
        ]


def _index_list_of_dict_by_key(seq, key):
    """ If you need to fetch repeatedly from name, you should index them by name (using a dictionary), this way get
    operations would be O(1) time. An idea:

    Source: https://stackoverflow.com/a/4391722/4562156

    :param seq: list of dictionaries
    :param key: key to index each dictionary within seq on
    :return: indexed list of dictionaries by `key`
    """
    return {d[key]: {**d, "index": idx} for (idx, d) in enumerate(seq)}
    # return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))


def split_by_comma(s):
    """ Split a string by comma, trim each resultant string element, and remove falsy-values.

    :param s: str to split by comma
    :return: list of provided string split by comma
    """
    return [i.strip() for i in s.split(",") if i]
