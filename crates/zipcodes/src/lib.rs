//! Query U.S. zipcodes without SQLite.
//!
//! The full zipcode dataset is embedded into the binary at compile time via
//! [`include_bytes!`] and lazily decompressed/parsed on first access, making
//! this crate suitable for constrained environments (AWS Lambda, containers)
//! with no runtime file I/O.

use std::io::prelude::*;
use std::sync::LazyLock;

use bzip2::read::BzDecoder;
use serde::{Deserialize, Serialize};

const ZIPCODE_LENGTH: usize = 5;

static ZIPCODE_BYTES_BZIP: &[u8] = include_bytes!("zips.json.bz2");

static ZIPCODES: LazyLock<Vec<Zipcode>> = LazyLock::new(|| {
    let mut decompressor = BzDecoder::new(ZIPCODE_BYTES_BZIP);
    let mut zipcode_json = String::new();
    decompressor
        .read_to_string(&mut zipcode_json)
        .expect("failed to decompress embedded zipcode database");
    serde_json::from_str::<Vec<Zipcode>>(&zipcode_json)
        .unwrap_or_else(|e| panic!("failed to deserialize zipcode database: {}", e))
});

/// Describes different types of errors with supplied zipcodes during parsing.
#[derive(thiserror::Error, Debug)]
pub enum Error {
    #[error("Invalid format, zipcode must be of the format: \"#####\" or \"#####-####\"")]
    InvalidFormat,
    #[error("Invalid characters, zipcode may only contain digits and \"-\".")]
    InvalidCharacters,
}

/// A result type where the error is an `Error`.
pub type Result<T> = std::result::Result<T, Error>;

/// A record in the zipcode database.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Zipcode {
    pub acceptable_cities: Vec<String>,
    pub active: bool,
    pub area_codes: Vec<String>,
    pub city: String,
    pub country: String,
    pub county: String,
    pub lat: String,
    pub long: String,
    pub state: String,
    pub timezone: String,
    pub unacceptable_cities: Vec<String>,
    pub world_region: String,
    pub zip_code: String,
    pub zip_code_type: String,
}

impl Zipcode {
    /// Compare a named field against a JSON value, mirroring the Python
    /// package's `filter_by(**kwargs)` semantics: an unknown field name or a
    /// type mismatch is simply not a match.
    pub fn field_matches(&self, field: &str, value: &serde_json::Value) -> bool {
        use serde_json::Value;
        fn eq_list(items: &[String], value: &Value) -> bool {
            match value {
                Value::Array(arr) => {
                    arr.len() == items.len()
                        && arr.iter().zip(items).all(|(v, s)| v.as_str() == Some(s))
                }
                _ => false,
            }
        }
        match field {
            "zip_code" => value.as_str() == Some(&self.zip_code),
            "zip_code_type" => value.as_str() == Some(&self.zip_code_type),
            "active" => value.as_bool() == Some(self.active),
            "city" => value.as_str() == Some(&self.city),
            "acceptable_cities" => eq_list(&self.acceptable_cities, value),
            "unacceptable_cities" => eq_list(&self.unacceptable_cities, value),
            "state" => value.as_str() == Some(&self.state),
            "county" => value.as_str() == Some(&self.county),
            "timezone" => value.as_str() == Some(&self.timezone),
            "area_codes" => eq_list(&self.area_codes, value),
            "world_region" => value.as_str() == Some(&self.world_region),
            "country" => value.as_str() == Some(&self.country),
            "lat" => value.as_str() == Some(&self.lat),
            "long" => value.as_str() == Some(&self.long),
            _ => false,
        }
    }
}

/// Determine whether a supplied zipcode matches any existing zipcode. The supplied
/// zipcode must be of the format: "#####", "#####-####", or "##### ####".
pub fn matching(zipcode: &str, zipcodes: Option<Vec<Zipcode>>) -> Result<Vec<Zipcode>> {
    let zipcode = clean_zipcode(zipcode)?;
    let zipcodes = zipcodes.as_deref().unwrap_or(&ZIPCODES);
    Ok(zipcodes
        .iter()
        .filter(|z| z.zip_code == zipcode)
        .cloned()
        .collect())
}

/// Returns true if the supplied zipcode exists in the database.
pub fn is_real(zipcode: &str) -> Result<bool> {
    Ok(!matching(zipcode, None)?.is_empty())
}

/// Return the zipcodes whose `zip_code` starts with the supplied prefix.
pub fn similar_to(prefix: &str, zipcodes: Option<Vec<Zipcode>>) -> Vec<Zipcode> {
    let zipcodes = zipcodes.as_deref().unwrap_or(&ZIPCODES);
    zipcodes
        .iter()
        .filter(|z| z.zip_code.starts_with(prefix))
        .cloned()
        .collect()
}

/// Return the zipcodes whose `zip_code` contains the supplied fragment anywhere.
pub fn contains(fragment: &str, zipcodes: Option<Vec<Zipcode>>) -> Vec<Zipcode> {
    let zipcodes = zipcodes.as_deref().unwrap_or(&ZIPCODES);
    zipcodes
        .iter()
        .filter(|z| z.zip_code.contains(fragment))
        .cloned()
        .collect()
}

/// Using a supplied list of filter-functions, return a filtered list of zipcodes.
///
/// By default, the supplied list of zipcodes is everything stored in the
/// database. However, an optional list of override zipcodes can be supplied.
pub fn filter_by<F>(filters: Vec<F>, zipcodes: Option<Vec<Zipcode>>) -> Result<Vec<Zipcode>>
where
    F: Fn(&Zipcode) -> bool,
{
    let zipcodes = zipcodes.as_deref().unwrap_or(&ZIPCODES);
    Ok(zipcodes
        .iter()
        .filter(|z| filters.iter().all(|f| f(z)))
        .cloned()
        .collect())
}

/// Return the zipcodes whose named fields equal the supplied JSON values.
///
/// All `(field, value)` pairs must match. An unknown field name matches
/// nothing, mirroring the Python package's `filter_by(**kwargs)`.
pub fn filter_by_fields(
    filters: &[(String, serde_json::Value)],
    zipcodes: Option<Vec<Zipcode>>,
) -> Vec<Zipcode> {
    let zipcodes = zipcodes.as_deref().unwrap_or(&ZIPCODES);
    zipcodes
        .iter()
        .filter(|z| {
            filters
                .iter()
                .all(|(field, value)| z.field_matches(field, value))
        })
        .cloned()
        .collect()
}

/// Calculate the great circle distance in miles between two points on the
/// earth, specified in decimal degrees.
pub fn haversine(lon1: f64, lat1: f64, lon2: f64, lat2: f64) -> f64 {
    let (lon1, lat1, lon2, lat2) = (
        lon1.to_radians(),
        lat1.to_radians(),
        lon2.to_radians(),
        lat2.to_radians(),
    );
    let dlon = lon2 - lon1;
    let dlat = lat2 - lat1;
    let a = (dlat / 2.0).sin().powi(2) + lat1.cos() * lat2.cos() * (dlon / 2.0).sin().powi(2);
    let c = 2.0 * a.sqrt().asin();
    let r = 3956.0; // Radius of earth in miles. Use 6371 for kilometers.
    c * r
}

/// Return the zipcodes within `radius_in_miles` of the supplied coordinates.
///
/// Records whose stored coordinates fail to parse are excluded.
pub fn filter_by_coordinates(
    lat: f64,
    long: f64,
    radius_in_miles: f64,
    zipcodes: Option<Vec<Zipcode>>,
) -> Vec<Zipcode> {
    let zipcodes = zipcodes.as_deref().unwrap_or(&ZIPCODES);
    zipcodes
        .iter()
        .filter(|z| match (z.lat.parse::<f64>(), z.long.parse::<f64>()) {
            (Ok(z_lat), Ok(z_long)) => haversine(z_long, z_lat, long, lat) <= radius_in_miles,
            _ => false,
        })
        .cloned()
        .collect()
}

/// Retrieve a list of all zipcodes in the database.
pub fn list_all() -> Vec<Zipcode> {
    ZIPCODES.clone()
}

/// Borrow the full embedded zipcode database without copying it.
pub fn database() -> &'static [Zipcode] {
    &ZIPCODES
}

fn clean_zipcode(zipcode: &str) -> Result<&str> {
    let zipcode = zipcode.trim();
    if zipcode.len() < ZIPCODE_LENGTH {
        return Err(Error::InvalidFormat);
    }
    let prefix = &zipcode[..ZIPCODE_LENGTH];
    if !prefix.chars().all(|c| c.is_ascii_digit()) {
        return Err(Error::InvalidCharacters);
    }
    Ok(prefix)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn should_find_real_zipcodes() {
        assert!(is_real("06903").unwrap());
        assert!(is_real("06905").unwrap());
    }

    #[test]
    fn should_not_find_fake_zipcodes() {
        assert!(!is_real("91239").unwrap());
    }

    #[test]
    fn should_return_no_zipcodes() {
        for zc in &["00000", "00000-0000", "00000 0000"] {
            assert!(matching(zc, None).unwrap().is_empty())
        }
    }

    #[test]
    fn should_match_zip_plus_four_to_base_zipcode() {
        assert_eq!(matching("06903-1234", None).unwrap().len(), 1);
    }

    #[test]
    fn should_fail_to_find_zipcodes_not_included_in_overrides() {
        let zc = "06903";
        matching(zc, None).unwrap();
        assert!(matching(zc, Some(matching("06904", None).unwrap()))
            .unwrap()
            .is_empty());
    }

    #[test]
    fn should_reject_invalid_zipcodes() {
        assert!(matches!(matching("123", None), Err(Error::InvalidFormat)));
        assert!(matches!(
            matching("1234a", None),
            Err(Error::InvalidCharacters)
        ));
    }

    #[test]
    fn should_include_county_field() {
        let zips = matching("06475", None).unwrap();
        assert_eq!(zips[0].county, "Middlesex County");
        assert_eq!(zips[0].city, "Old Saybrook");
    }

    #[test]
    fn should_find_similar_zipcodes_by_prefix() {
        let zips = similar_to("1018", None);
        assert_eq!(
            zips.iter().map(|z| z.zip_code.as_str()).collect::<Vec<_>>(),
            vec!["10184", "10185"]
        );
    }

    #[test]
    fn should_find_zipcodes_containing_fragment() {
        assert!(contains("0185", None).iter().any(|z| z.zip_code == "10185"));
    }

    #[test]
    fn should_filter_by_fields() {
        let filters = vec![
            ("active".to_string(), json!(true)),
            ("city".to_string(), json!("Windsor")),
        ];
        let windsor = filter_by_fields(&filters, None);
        assert!(!windsor.is_empty());
        assert!(windsor.iter().all(|z| z.active && z.city == "Windsor"));
        assert_eq!(similar_to("2", Some(windsor)).len(), 3);
    }

    #[test]
    fn should_not_match_unknown_filter_fields() {
        let filters = vec![("nonexistent".to_string(), json!("x"))];
        assert!(filter_by_fields(&filters, None).is_empty());
    }

    #[test]
    fn should_filter_by_coordinates() {
        // Old Saybrook, CT (41.3015, -72.3879); a tight radius isolates it.
        let nearby = filter_by_coordinates(41.3015, -72.3879, 1.0, None);
        assert!(nearby.iter().any(|z| z.zip_code == "06475"));
        // Wrong hemisphere (positive longitude) is nowhere near any US zipcode.
        assert!(filter_by_coordinates(42.2529, 71.0023, 100.0, None).is_empty());
    }

    #[test]
    fn haversine_known_distance() {
        // NYC (40.7128, -74.0060) to LA (34.0522, -118.2437) is ~2445 miles.
        let d = haversine(-74.0060, 40.7128, -118.2437, 34.0522);
        assert!((d - 2445.0).abs() < 15.0, "distance was {}", d);
    }
}
