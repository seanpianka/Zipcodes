# Zipcodes

[![Docs](https://docs.rs/zipcodes/badge.svg)](https://docs.rs/zipcodes)
[![Crates.io](https://img.shields.io/crates/v/zipcodes.svg?maxAge=2592000)](https://crates.io/crates/zipcodes)![Crates.io](https://img.shields.io/crates/d/zipcodes)![MSRV](https://img.shields.io/badge/MSRV-1.82-blue.svg)

`Zipcodes` is a simple library for querying U.S. zipcodes. The full dataset is
embedded into the library at compile time (via `include_bytes!`) and lazily
decompressed on first access — no files, no network, no database.

This crate and the [`zipcodes` Python package](https://pypi.org/project/zipcodes/)
are built from the same source: <https://github.com/seanpianka/zipcodes>.

The zipcode data is refreshed automatically every month by CI in the source
repository.

The minimum supported Rust version (MSRV) is `1.82`.

## Installation

```console
$ cargo add zipcodes
```

## Quick Start

```rust
fn main() -> zipcodes::Result<()> {
    // Find zipcodes matching "77429". Zip+4 inputs like "77429-1145" work too.
    let results = zipcodes::matching("77429", None)?;

    // The `matching` function returns a `Vec`, as a 5-digit zipcode
    // isn't guaranteed to be unique across different localities.
    if let Some(zip) = results.first() {
        println!("{:#?}", zip);
    }

    Ok(())
}
```

### Example Output

```text
Zipcode {
    acceptable_cities: [],
    active: true,
    area_codes: [
        "281",
        "346",
        "713",
        "832",
    ],
    city: "Cypress",
    country: "US",
    county: "Harris County",
    lat: "29.9857",
    long: "-95.6548",
    state: "TX",
    timezone: "America/Chicago",
    unacceptable_cities: [],
    world_region: "NA",
    zip_code: "77429",
    zip_code_type: "STANDARD",
}
```

## Examples

### Validating a Zipcode

```rust
use zipcodes::is_real;

fn main() -> zipcodes::Result<()> {
    assert!(is_real("06903")?);
    assert!(!is_real("00000")?);
    Ok(())
}
```

### Prefix and Substring Search

```rust
// All zipcodes starting with "1018"
let zips = zipcodes::similar_to("1018", None);

// All zipcodes containing "018" anywhere
let zips = zipcodes::contains("018", None);
```

### Advanced Filtering

The `filter_by()` function allows for powerful, custom queries using a vector
of closures.

```rust
use zipcodes::{filter_by, Zipcode};

fn main() -> zipcodes::Result<()> {
    // Find all active "PO BOX" zipcodes in Massachusetts.
    let filters: Vec<Box<dyn Fn(&Zipcode) -> bool>> = vec![
        Box::new(|z| z.state == "MA"),
        Box::new(|z| z.zip_code_type == "PO BOX"),
        Box::new(|z| z.active),
    ];

    let ma_po_boxes = filter_by(filters, None)?;
    println!("Found {} active PO Box zipcodes in Massachusetts.", ma_po_boxes.len());
    Ok(())
}
```

### Geographic Queries

```rust
// All zipcodes within 5 miles of Old Saybrook, CT.
let nearby = zipcodes::filter_by_coordinates(41.3015, -72.3879, 5.0, None);

// Great-circle distance in miles between two (lon, lat) points.
let miles = zipcodes::haversine(-74.0060, 40.7128, -118.2437, 34.0522);
```

### Listing All Zipcodes

```rust
// Borrow the database without copying it...
let all = zipcodes::database();

// ...or get an owned copy.
let all_owned = zipcodes::list_all();
println!("There are {} zipcodes loaded in the database.", all.len());
```

## Zipcode Data

The zipcode data is embedded directly into the library at compile time via
`include_bytes!` and decompressed lazily on first use. This ensures fast
lookups at runtime without needing to read from a file or an external
database.

The dataset is assembled from unitedstateszipcodes.org (base data), the USPS
ZIP Locale Detail file (active delivery ZIPs, public domain), and
[GeoNames](https://www.geonames.org/) postal data (GPS coordinates, licensed
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)). It is refreshed
monthly by an automated workflow in the source repository.

## Contributing

Have an idea for a new feature? Feel free to open a pull request at
<https://github.com/seanpianka/zipcodes> and contribute!
