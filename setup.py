# Always prefer setuptools over distutils
from setuptools import setup, find_packages

with open("README.md") as f:
    readme = f.read()

with open("VERSION.txt") as f:
    version = f.read()

setup(
    name="zipcodes",
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html

    # remove whitespace (some IDE's add trailing newlines automatically)
    version=version.strip(),
    description="Query U.S. state zipcodes without SQLite.",
    long_description=readme,
    long_description_content_type="text/markdown",
    # The project's main homepage.
    url="https://github.com/seanpianka/zipcodes",
    # Author details
    author="Sean Pianka",
    author_email="pianka@eml.cc",
    # Choose your license
    license="MIT",
    packages=find_packages(exclude=("ci", "tests")),
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 5 - Production/Stable",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    # What does your project relate to?
    keywords="zipcode zip code us state query filter validate sqlite",
    include_package_data=True,
)
