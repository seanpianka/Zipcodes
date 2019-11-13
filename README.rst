Zipcodes
========

Zipcodes is a package for Python 3 and Python 2.7 which supports lookup and filtering of zipcode data for the U.S.

.. image:: https://pepy.tech/badge/zipcodes

Installation
============

.. code:: bash

    $ pip install zipcodes


Synopsis
========

In search for a package to lookup U.S. zipcode data, `zipcode <https://github.com/buckmaxwell/zipcode>`__ is one of
the top results. However, if you're deploying into a cloud (and in my case, serverless) environment like AWS Lambda,
then the above package, which depends on SQLite, is not an option due to AWS Lambda's lack of runtime SQLite support.

The data used in building `zipcodes/zips.json.bz2` can be found under `build/app/data/`. The scripts necessary to
reproduce and build `zipcodes/zips.json.bz2` can be found under `build/app/__init__.py`.

The tests are defined in and are generated from a custom, declarative format.

Below is the expected usage of this package and a demonstration of
supported functionality.

.. code:: python

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
