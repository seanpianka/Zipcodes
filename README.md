# Zipcodes
A lightweight U.S. zip-code validation package for Python (2 and 3).

## Synopsis

Below is the expected usage of this package and a demonstration of supported functionality.

```python
>>> import zipcodes

>>> print(zipcodes.get_zipcode('06469-1145'))
[{'zip_code': '06469', 'zip_code_type': 'STANDARD', 'city': 'MOODUS', 'state': 'CT', 'world_region': 'NA', 'country': 'US'}]

>>> print(zipcodes.get_zipcode('06469'))
[{'zip_code': '06469', 'zip_code_type': 'STANDARD', 'city': 'MOODUS', 'state': 'CT', 'world_region': 'NA', 'country': 'US'}]

>>> print(zipcodes.get_zipcode('06463'))
None

>>> print(zipcodes.is_valid_zipcode('06469-1145'))
True
```

## Method Documentation

### get_zipcode
    Retrieve additional information about a zip-code such as the associated
    city and state. The provided zipcode can either be of the form '06469' or
    '06469-1154'. Zip-5-codes and Zip-9-codes are both supported.

    Parameters
    ----------
    zipcode : str
        The zip-code to find more information about.

    Returns
    -------
    dict
        Dictionary containing "zip_code", "zip_code_type", "city", "state",
        "world_region", and "country" as keys. Example:
```python
>>> {"zip_code": "00705",
     "zip_code_type": "STANDARD",
     "city": "AIBONITO",
     "state": "PR",
     "world_region": "NA",
     "country": "US"}
```

    Raises
    ------
    TypeError
        When the zip-code is not a string or contains characters other than
        digits and "-".


### is_valid_zipcode
    Determine whether a given U.S. zip-code is valid. The provided zipcode
    can either be of the form '06469' or '06469-1154'. Zip-5-codes and
    Zip-9-codes are both supported.

    Parameters
    ----------
    zipcode : str
        The zip-code to test for validity.

    Returns
    -------
    bool
        Whether the provided zip-code is valid.

    Raises
    ------
    TypeError
        When the zip-code is not a string or contains characters other than
        digits and "-".
