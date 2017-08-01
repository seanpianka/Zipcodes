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

    >>> import zipcodes

    >>> print(zipcodes.matching('06469'))
    [{'zip_code': '06469', 'zip_code_type': 'STANDARD', 'city': 'MOODUS', 'state': 'CT', 'world_region': 'NA', 'country': 'US'}]

    >>> print(zipcodes.matching('06469-1145'))
    [{'zip_code': '06469', 'zip_code_type': 'STANDARD', 'city': 'MOODUS', 'state': 'CT', 'world_region': 'NA', 'country': 'US'}]

    >>> print(zipcodes.matching('06463'))
    None

    >>> print(zipcodes.is_valid('06463'))
    False

    >>> print(zipcodes.is_valid('06469'))
    True

    >>> print(zipcodes.similar_to('0646'))
    [{'zip_code': '06460', 'zip_code_type': 'STANDARD', 'city': 'MILFORD', 'state': 'CT', 'world_region': 'NA', 'country': 'US'}, {'zip_code': '06461', 'zip_code_type': 'STANDARD', 'city': 'MILFORD', 'state': 'CT', 'world_region': 'NA', 'country': 'US'}, {'zip_code': '06467', 'zip_code_type': 'PO BOX', 'city': 'MILLDALE', 'state': 'CT', 'world_region': 'NA', 'country': 'US'}, {'zip_code': '06468', 'zip_code_type': 'STANDARD', 'city': 'MONROE', 'state': 'CT', 'world_region': 'NA', 'country': 'US'}, {'zip_code': '06469', 'zip_code_type': 'STANDARD', 'city': 'MOODUS', 'state': 'CT', 'world_region': 'NA', 'country': 'US'}]

