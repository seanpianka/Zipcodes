# Zipcodes

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/zipcodes)
[![PyPI](https://img.shields.io/pypi/v/zipcodes)](https://pypi.org/project/zipcodes/)
[![crates.io](https://img.shields.io/crates/v/zipcodes)](https://crates.io/crates/zipcodes)
[![Downloads](https://static.pepy.tech/badge/zipcodes/month)](https://pepy.tech/project/zipcodes)
[![Contributors](https://img.shields.io/github/contributors/seanpianka/zipcodes.svg)](https://github.com/seanpianka/zipcodes/graphs/contributors)

Zipcodes is a simple library for querying U.S. zipcodes. No SQLite, no
network, no runtime data files — the full dataset is embedded in the package.

Since 2.0, the library is implemented in Rust and published from a single
codebase as both the [`zipcodes` Python package](https://pypi.org/project/zipcodes/)
and the [`zipcodes` Rust crate](https://crates.io/crates/zipcodes). The Python
API is a drop-in replacement for 1.x — same functions, same dicts, same
exceptions — just faster:

| Operation | 1.x (pure Python) | 2.0 (Rust) |
|---|---|---|
| `import zipcodes` | ~330 ms (loads dataset) | ~5 ms (dataset loads lazily on first query, ~200 ms) |
| `is_real("06903")` | ~4.2 ms | ~0.03 ms |
| `matching("77429")` | ~4.2 ms | ~0.3 ms |
| `similar_to("1018")` | ~7.2 ms | ~0.3 ms |
| `filter_by(state="TX")` | ~9.7 ms | ~3.7 ms |

```python
>>> import zipcodes
>>> assert zipcodes.is_real('77429')
>>> assert len(zipcodes.similar_to('7742')) != 0
>>> exact_zip = zipcodes.matching('77429')[0]
>>> filtered_zips = zipcodes.filter_by(city="Cypress", state="TX")
>>> assert exact_zip in filtered_zips
>>> pprint.pprint(exact_zip)
{'acceptable_cities': [],
 'active': True,
 'area_codes': ['281', '346', '713', '832'],
 'city': 'Cypress',
 'country': 'US',
 'county': 'Harris County',
 'lat': '29.9766',
 'long': '-95.6358',
 'state': 'TX',
 'timezone': 'America/Chicago',
 'unacceptable_cities': [],
 'world_region': 'NA',
 'zip_code': '77429',
 'zip_code_type': 'STANDARD'}
```

The zipcode data is refreshed automatically every month — see
[Zipcode Data](#zipcode-data).

## Installation

### Python

```console
$ python -m pip install zipcodes
```

Zipcodes 2.x supports Python 3.9+ and ships prebuilt wheels for Linux
(x86_64, aarch64, musl), macOS, and Windows. Installing from the source
distribution requires a Rust toolchain. Python 2.6+/3.2+ users are
automatically served the pure-Python 1.3.0 release by pip.

### Rust

```console
$ cargo add zipcodes
```

### New in 2.0

- Implemented in Rust; the dataset is compiled into the extension module and
  decompressed lazily on first query, so `import zipcodes` is effectively free.
- New functions: `contains`, `filter_by_state`, `filter_by_city`,
  `filter_by_county`, `filter_by_timezone`, `filter_by_zip_code_type`,
  `filter_by_coordinates`, and `haversine`.
- `is_valid` now actually emits its `DeprecationWarning` (in 1.x it raised
  `AttributeError`); use `is_real`.
- PyInstaller users no longer need `--add-data` for `zips.json.bz2` — there is
  no data file anymore.
- Behavioral notes for upgraders: query results are fresh dicts (mutating a
  result no longer mutates the shared database list), and
  `filter_by(active=1)` no longer matches `active=True` (pass a bool).

## Zipcode Data

The embedded dataset (`crates/zipcodes/src/zips.json.bz2`) is assembled from
three sources:

- **[unitedstateszipcodes.org](https://www.unitedstateszipcodes.org)** — the
  rich base data (city aliases, zip type, area codes, county, timezone),
  committed in-repo as `scripts/data/zip_code_database.csv`. Its bot
  protection prevents automated downloads, so this file is refreshed manually
  on occasion.
- **[GeoNames](https://www.geonames.org/)** (`download.geonames.org/export/zip/US.zip`) —
  GPS coordinates, fetched fresh on every update. Licensed
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- **USPS ZIP Locale Detail** ([postalpro.usps.com](https://postalpro.usps.com/ZIP_Locale_Detail)) —
  the authoritative list of active delivery ZIPs, fetched fresh on every
  update and used to add zipcodes missing from the base CSV
  ([#23](https://github.com/seanpianka/Zipcodes/issues/23)). Public domain.

A GitHub Actions workflow ([`update-data.yml`](.github/workflows/update-data.yml))
rebuilds the dataset on the 1st of every month
([#7](https://github.com/seanpianka/Zipcodes/issues/7)). If anything changed,
it opens a pull request with a summary of added/removed/modified records;
merging that PR tags a patch release, which publishes to PyPI and crates.io
automatically.

To rebuild the dataset manually:

```shell script
$ pip install xlrd
$ curl -fsSL https://download.geonames.org/export/zip/US.zip -o /tmp/geonames_us.zip
$ # download the .xls linked from https://postalpro.usps.com/ZIP_Locale_Detail
$ python scripts/update_zipcode_dataset.py \
    --base scripts/data/zip_code_database.csv \
    --gps scripts/data/zip-codes-database-FREE.csv \
    --geonames-zip /tmp/geonames_us.zip \
    --usps-xls /tmp/usps_zip_locale.xls \
    --output-bz2 crates/zipcodes/src/zips.json.bz2 \
    --summary-output /tmp/change_summary.json
```

## Tests

The tests are defined in a declarative, table-based format that generates test
cases.

```shell script
$ cargo test                    # Rust unit tests
$ python tests/__init__.py      # Python suite (or: pytest tests/)
```

## Examples

```python
>>> from pprint import pprint
>>> import zipcodes

>>> # Simple zip-code matching.
>>> pprint(zipcodes.matching('77429'))
[{'acceptable_cities': [],
  'active': True,
  'area_codes': ['281', '346', '713', '832'],
  'city': 'Cypress',
  'country': 'US',
  'county': 'Harris County',
  'lat': '29.9766',
  'long': '-95.6358',
  'state': 'TX',
  'timezone': 'America/Chicago',
  'unacceptable_cities': [],
  'world_region': 'NA',
  'zip_code': '77429',
  'zip_code_type': 'STANDARD'}]


>>> # Handles Zip+4 zip-codes nicely. :)
>>> pprint(zipcodes.matching('77429-1145'))
[{'acceptable_cities': [],
  'active': True,
  'area_codes': ['281', '346', '713', '832'],
  'city': 'Cypress',
  'country': 'US',
  'county': 'Harris County',
  'lat': '29.9766',
  'long': '-95.6358',
  'state': 'TX',
  'timezone': 'America/Chicago',
  'unacceptable_cities': [],
  'world_region': 'NA',
  'zip_code': '77429',
  'zip_code_type': 'STANDARD'}]

>>> # Will try to handle invalid zip-codes gracefully...
>>> print(zipcodes.matching('06463'))
[]

>>> # Until it cannot.
>>> zipcodes.matching('0646a')
Traceback (most recent call last):
  ...
ValueError: Invalid characters, zipcode may only contain digits and "-".

>>> zipcodes.matching('064690')
Traceback (most recent call last):
  ...
ValueError: Invalid format, zipcode must be of the format: "#####" or "#####-####"

>>> zipcodes.matching(None)
Traceback (most recent call last):
  ...
TypeError: Invalid type, zipcode must be a string.

>>> # Whether the zip-code exists within the database.
>>> print(zipcodes.is_real('06463'))
False

>>> # How handy!
>>> print(zipcodes.is_real('06469'))
True

>>> # Search for zipcodes that begin with a pattern.
>>> pprint(zipcodes.similar_to('1018'))
[{'acceptable_cities': [],
  'active': False,
  'area_codes': ['212'],
  'city': 'New York',
  'country': 'US',
  'county': 'New York County',
  'lat': '40.71',
  'long': '-74',
  'state': 'NY',
  'timezone': 'America/New_York',
  'unacceptable_cities': ['J C Penney'],
  'world_region': 'NA',
  'zip_code': '10184',
  'zip_code_type': 'UNIQUE'},
 {'acceptable_cities': [],
  'active': True,
  'area_codes': ['212'],
  'city': 'New York',
  'country': 'US',
  'county': 'New York County',
  'lat': '40.7808',
  'long': '-73.9772',
  'state': 'NY',
  'timezone': 'America/New_York',
  'unacceptable_cities': ['Manhattan', 'New York City', 'NY', 'Ny City', 'Nyc'],
  'world_region': 'NA',
  'zip_code': '10185',
  'zip_code_type': 'PO BOX'}]

>>> # Use filter_by to filter a list of zip-codes by specific attribute->value pairs.
>>> pprint(zipcodes.filter_by(city="Old Saybrook"))
[{'acceptable_cities': [],
  'active': True,
  'area_codes': ['860', '959'],
  'city': 'Old Saybrook',
  'country': 'US',
  'county': 'Middlesex County',
  'lat': '41.2913',
  'long': '-72.385',
  'state': 'CT',
  'timezone': 'America/New_York',
  'unacceptable_cities': ['Fenwick'],
  'world_region': 'NA',
  'zip_code': '06475',
  'zip_code_type': 'STANDARD'}]

>>> # Arbitrary nesting of similar_to and filter_by calls, allowing for great precision while filtering.
>>> pprint([z['zip_code'] for z in zipcodes.similar_to('2', zips=zipcodes.filter_by(active=True, city='Windsor'))])
['23487', '27983', '29856']

>>> # Find zipcodes within a radius (miles) of a coordinate.
>>> pprint([z['zip_code'] for z in zipcodes.filter_by_coordinates(41.3015, -72.3879, 5)])
['06371', '06409', '06426', '06442', '06475', '06498']

>>> # Have any other ideas? Make a pull request and start contributing today!
>>> # Made with love by Sean Pianka
```

## Repository layout

This repository builds both packages from one Rust core:

- `crates/zipcodes` — the core library, published to
  [crates.io](https://crates.io/crates/zipcodes).
- `crates/zipcodes-py` — PyO3 bindings (not published to crates.io).
- `python/zipcodes` — the thin Python compatibility layer; together with the
  bindings it forms the [PyPI package](https://pypi.org/project/zipcodes/),
  built with [maturin](https://github.com/PyO3/maturin).
