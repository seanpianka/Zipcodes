# Zipcodes

Zipcodes is a simple library for querying U.S. zipcodes.

The Python `sqlite3` module is not required in order to use this package.

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
  'area_codes': ['281', '832'],
  'city': 'Cypress',
  'country': 'US',
  'county': 'Harris County',
  'lat': '29.9857',
  'long': '-95.6548',
  'state': 'TX',
  'timezone': 'America/Chicago',
  'unacceptable_cities': [],
  'world_region': 'NA',
  'zip_code': '77429',
  'zip_code_type': 'STANDARD'}[
```

⚠️ The zipcode data was last updated on: **Oct. 3, 2021** ⚠️

[![Downloads](https://pepy.tech/badge/zipcodes/month)](https://pepy.tech/project/zipcodes/month)
[![Supported Versions](https://img.shields.io/pypi/pyversions/zipcodes.svg)](https://pypi.org/project/zipcodes)
[![Contributors](https://img.shields.io/github/contributors/seanpianka/zipcodes.svg)](https://github.com/seanpianka/zipcodes/graphs/contributors)


## Installation

Zipcodes is available on PyPI:

```console
$ python -m pip install zipcodes
```

Zipcodes supports Python 2.6+ and Python 3.2+.

### Compiling with PyInstaller

Add a data file to your PyInstaller bundle with the [`--add-data`](https://pyinstaller.readthedocs.io/en/stable/spec-files.html#adding-data-files) flag.


#### Linux and MacOS
`--add-data "<path-to-package-install>/zipcodes/zips.json.bz2:zipcodes"`

#### Windows
`--add-data "<path-to-package-install>\zipcodes\zips.json.bz2;zipcodes"`

## Zipcode Data

The build script for the zipcode data outputs a JSON file containing all the zipcode data and zipped using bzip2. The data sources are stored under `build/app/data`. 

Build the zipcode data for distribution: 

```shell script
$ build/app/__init__.py # outputs `zipcodes/zips.json.bz2`
```


## Tests

The tests are defined in a declarative, table-based format that generates test
cases. 

Run the tests directly:

```shell script
$ python tests/__init__.py 
```

## Examples

```python
>>> from pprint import pprint
>>> import zipcodes

>>> # Simple zip-code matching.
>>> pprint(zipcodes.matching('77429'))
[{'acceptable_cities': [],
  'active': True,
  'area_codes': ['281', '832'],
  'city': 'Cypress',
  'country': 'US',
  'county': 'Harris County',
  'lat': '29.9857',
  'long': '-95.6548',
  'state': 'TX',
  'timezone': 'America/Chicago',
  'unacceptable_cities': [],
  'world_region': 'NA',
  'zip_code': '77429',
  'zip_code_type': 'STANDARD'}]


>>> # Handles of Zip+4 zip-codes nicely. :)
>>> pprint(zipcodes.matching('77429-1145'))
[{'acceptable_cities': [],
  'active': True,
  'area_codes': ['281', '832'],
  'city': 'Cypress',
  'country': 'US',
  'county': 'Harris County',
  'lat': '29.9857',
  'long': '-95.6548',
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
TypeError: Invalid characters, zipcode may only contain digits and "-".

>>> zipcodes.matching('064690')
Traceback (most recent call last):
  ...
TypeError: Invalid format, zipcode must be of the format: "#####" or "#####-####"

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
  'lat': '40.7143',
  'long': '-74.0067',
  'state': 'NY',
  'timezone': 'America/New_York',
  'unacceptable_cities': [],
  'world_region': 'NA',
  'zip_code': '10185',
  'zip_code_type': 'PO BOX'}]

>>> # Use filter_by to filter a list of zip-codes by specific attribute->value pairs.
>>> pprint(zipcodes.filter_by(city="Old Saybrook"))
[{'acceptable_cities': [],
  'active': True,
  'area_codes': ['860'],
  'city': 'Old Saybrook',
  'country': 'US',
  'county': 'Middlesex County',
  'lat': '41.3015',
  'long': '-72.3879',
  'state': 'CT',
  'timezone': 'America/New_York',
  'unacceptable_cities': ['Fenwick'],
  'world_region': 'NA',
  'zip_code': '06475',
  'zip_code_type': 'STANDARD'}]

>>> # Arbitrary nesting of similar_to and filter_by calls, allowing for great precision while filtering.
>>> pprint(zipcodes.similar_to('2', zips=zipcodes.filter_by(active=True, city='Windsor')))
[{'acceptable_cities': [],
  'active': True,
  'area_codes': ['757'],
  'city': 'Windsor',
  'country': 'US',
  'county': 'Isle of Wight County',
  'lat': '36.8628',
  'long': '-76.7143',
  'state': 'VA',
  'timezone': 'America/New_York',
  'unacceptable_cities': [],
  'world_region': 'NA',
  'zip_code': '23487',
  'zip_code_type': 'STANDARD'},
 {'acceptable_cities': ['Askewville'],
  'active': True,
  'area_codes': ['252'],
  'city': 'Windsor',
  'country': 'US',
  'county': 'Bertie County',
  'lat': '35.9942',
  'long': '-76.9422',
  'state': 'NC',
  'timezone': 'America/New_York',
  'unacceptable_cities': [],
  'world_region': 'NA',
  'zip_code': '27983',
  'zip_code_type': 'STANDARD'},
 {'acceptable_cities': [],
  'active': True,
  'area_codes': ['803'],
  'city': 'Windsor',
  'country': 'US',
  'county': 'Aiken County',
  'lat': '33.4730',
  'long': '-81.5132',
  'state': 'SC',
  'timezone': 'America/New_York',
  'unacceptable_cities': [],
  'world_region': 'NA',
  'zip_code': '29856',
  'zip_code_type': 'STANDARD'}]

>>> # Have any other ideas? Make a pull request and start contributing today!
>>> # Made with love by Sean Pianka
```
