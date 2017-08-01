Zipcodes
========

A lightweight U.S. zip-code validation package for Python (2 and 3).
This package was built as
`zipcode <https://github.com/buckmaxwell/zipcode>`__ provided too much
functionality and relied on ``sqlite3``, which is not available on
platforms such as *AWS Lambda*. While more difficult to add additional
zip-codes, this package provides the essential functionality of zip-code
validation with fewer dependencies and minimal working logic.

Contributions are welcome!

Synopsis
========

Below is the expected usage of this package and a demonstration of
supported functionality.

.. code:: python

    >>> from pprint import pprint
    >>> import zipcodes

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

    >>> print(zipcodes.matching('06463'))
    []

    >>> print(zipcodes.is_valid('06463'))
    False

    >>> print(zipcodes.is_valid('06469'))
    True

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

    >>> pprint(zipcodes.filter_by(zipcodes.list_all(), active=True, city='WINDSOR'))
    [{'active': True,
      'city': 'WINDSOR',
      'country': 'US',
      'lat': 44.31,
      'long': -69.58,
      'state': 'ME',
      'world_region': 'NA',
      'zip_code': '04363',
      'zip_code_type': 'STANDARD'},
     {'active': True,
      'city': 'WINDSOR',
      'country': 'US',
      'lat': 43.48,
      'long': -72.42,
      'state': 'VT',
      'world_region': 'NA',
      'zip_code': '05089',
      'zip_code_type': 'STANDARD'},
    ... # remaining results truncated for readability...
    ]

    >>> pprint(zipcodes.similar_to('2', zips=zipcodes.filter_by(zipcodes.list_all(), active=True, city='WINDSOR')))
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



