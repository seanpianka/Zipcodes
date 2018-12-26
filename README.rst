Zipcodes
========

A lightweight U.S. zip-code validation package for Python (2 and 3).
This package was built as
`zipcode <https://github.com/buckmaxwell/zipcode>`__ provided too much
functionality and relied on ``sqlite3``, which is not available on
platforms such as *AWS Lambda*. While more difficult to add additional
zip-codes, this package provides the essential functionality of zip-code
validation with fewer dependencies and minimal working logic.

.. image:: https://pepy.tech/badge/zipcodes

Contributions are welcome!

Installation
============

.. code:: bash

    $ pip install zipcodes


Synopsis
========

Below is the expected usage of this package and a demonstration of
supported functionality.

.. code:: python

    >>> from pprint import pprint
    >>> import zipcodes

    >>> # Simple zip-code matching.
    >>> pprint(zipcodes.matching('77429'))
    [{'zip_code': '77429',
      'zip_code_type': 'STANDARD',
      'city': 'CYPRESS',
      'state': 'TX',
      'lat': 29.96,
      'long': -95.69,
      'world_region': 'NA',
      'country': 'US',
      'active': True}]

    >>> # Handles of Zip+4 zip-codes nicely. :)
    >>> pprint(zipcodes.matching('77429-1145'))
    [{'zip_code': '77429',
      'zip_code_type': 'STANDARD',
      'city': 'CYPRESS',
      'state': 'TX',
      'lat': 29.96,
      'long': -95.69,
      'world_region': 'NA',
      'country': 'US',
      'active': True}]

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
    >>> pprint(zipcodes.similar_to('0643'))
    [{'active': True,
      'city': 'GUILFORD',
      'country': 'US',
      'lat': 41.28,
      'long': -72.67,
      'state': 'CT',
      'world_region': 'NA',
      'zip_code': '06437',
      'zip_code_type': 'STANDARD'},

     {'active': True,
      'city': 'HADDAM',
      'country': 'US',
      'lat': 41.45,
      'long': -72.5,
      'state': 'CT',
      'world_region': 'NA',
      'zip_code': '06438',
      'zip_code_type': 'STANDARD'},
    ... # remaining results truncated for readability...
    ]

    >>> # Use filter_by to filter a list of zip-codes by specific attribute->value pairs.
    >>> pprint(zipcodes.filter_by(city="WINDSOR", state="CT"))
    [{"zip_code": "06006",
      "zip_code_type": "UNIQUE",
      "city": "WINDSOR",
      "state": "CT",
      "lat": 41.85,
      "long": -72.65,
      "world_region": "NA",
      "country": "US",
      "active": True },

     {"zip_code": "06095",
      "zip_code_type": "STANDARD",
      "city": "WINDSOR",
      "state": "CT",
      "lat": 41.85,
      "long": -72.65,
      "world_region": "NA",
      "country": "US",
      "active": True},
    ],

    >>> # Arbitrary nesting of similar_to and filter_by calls, allowing for great precision while filtering.
    >>> pprint(zipcodes.similar_to('2', zips=zipcodes.filter_by(active=True, city='WINDSOR')))
    [{'active': True,
      'city': 'WINDSOR',
      'country': 'US',
      'lat': 33.48,
      'long': -81.51,
      'state': 'SC',
      'world_region': 'NA',
      'zip_code': '29856',
      'zip_code_type': 'STANDARD'},
     {'active': True,
      'city': 'WINDSOR',
      'country': 'US',
      'lat': 36.8,
      'long': -76.73,
      'state': 'VA',
      'world_region': 'NA',
      'zip_code': '23487',
      'zip_code_type': 'STANDARD'},
     {'active': True,
      'city': 'WINDSOR',
      'country': 'US',
      'lat': 36.0,
      'long': -76.94,
      'state': 'NC',
      'world_region': 'NA',
      'zip_code': '27983',
      'zip_code_type': 'STANDARD'}]

    >>> # Have any other ideas? Make a pull request and start contributing today!
    >>> # Made with love by Sean Pianka
