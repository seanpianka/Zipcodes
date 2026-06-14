//! Native module `zipcodes._zipcodes`.
//!
//! Database scans delegate to the `zipcodes` crate's query functions, and the
//! `zips=` override path (chaining filters over previously returned dicts) is
//! filtered here in Rust, so the crate is the single implementation of scan
//! semantics. The Python-facing compat layer (argument validation, exact 1.x
//! exception messages) lives in `python/zipcodes/__init__.py`.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBool, PyDict, PyList};
use serde_json::Value;
use zipcodes::Zipcode;

/// Map a core validation error to the 1.x `ValueError`, preserving its message
/// verbatim. A free helper rather than `impl From<zipcodes::Error> for PyErr`
/// because both types are foreign to this crate (orphan rule).
fn to_py_err(e: zipcodes::Error) -> PyErr {
    PyValueError::new_err(e.to_string())
}

/// Build a dict in `zipcodes::FIELD_ORDER` order (the 1.x pure-Python key order).
///
/// This is hand-written rather than derived from `serde_json::to_value` on
/// purpose: a serde-based builder iterating `FIELD_ORDER` cannot drift from the
/// struct, but it allocates a `Map<String, Value>` per record and measured ~60%
/// slower on `list_all()` (which materializes ~42k dicts) — past our tolerance.
/// Drift is instead caught by tests, not by construction: `FIELD_ORDER` is
/// pinned to the struct by `field_order_matches_struct` in the core crate, and
/// this builder's output is pinned to `FIELD_ORDER` by `tests/test_schema.py`.
/// Keep the `set_item` order identical to `FIELD_ORDER`.
fn to_dict<'py>(py: Python<'py>, z: &Zipcode) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("zip_code", &z.zip_code)?;
    dict.set_item("zip_code_type", &z.zip_code_type)?;
    dict.set_item("active", z.active)?;
    dict.set_item("city", &z.city)?;
    dict.set_item("acceptable_cities", &z.acceptable_cities)?;
    dict.set_item("unacceptable_cities", &z.unacceptable_cities)?;
    dict.set_item("state", &z.state)?;
    dict.set_item("county", &z.county)?;
    dict.set_item("timezone", &z.timezone)?;
    dict.set_item("area_codes", &z.area_codes)?;
    dict.set_item("world_region", &z.world_region)?;
    dict.set_item("country", &z.country)?;
    dict.set_item("lat", &z.lat)?;
    dict.set_item("long", &z.long)?;
    Ok(dict)
}

/// Convert crate query results to a list of dicts (1.x field order).
fn to_pylist<'py>(py: Python<'py>, zips: &[Zipcode]) -> PyResult<Bound<'py, PyList>> {
    let dicts = zips
        .iter()
        .map(|z| to_dict(py, z))
        .collect::<PyResult<Vec<_>>>()?;
    PyList::new(py, dicts)
}

/// Filter a caller-supplied list of dicts, returning the matching items as-is
/// (no deserialization round-trip, no re-ordering of caller keys). The
/// predicate treats any per-item failure (missing key, non-dict item,
/// inconvertible value) as "not a match".
fn filter_pylist<'py, F>(
    py: Python<'py>,
    zips: &Bound<'py, PyList>,
    pred: F,
) -> PyResult<Bound<'py, PyList>>
where
    F: Fn(&Bound<'py, PyAny>) -> bool,
{
    let matches: Vec<_> = zips.iter().filter(|item| pred(item)).collect();
    PyList::new(py, matches)
}

/// Extract `item[key]` as a string; `None` on a missing key or non-string value.
fn get_str(item: &Bound<'_, PyAny>, key: &str) -> Option<String> {
    item.get_item(key).ok()?.extract::<String>().ok()
}

/// Extract `item[key]` as a coordinate, accepting str or float values as the
/// 1.x `float(z["lat"])` did.
fn get_coordinate(item: &Bound<'_, PyAny>, key: &str) -> Option<f64> {
    let value = item.get_item(key).ok()?;
    if let Ok(f) = value.extract::<f64>() {
        return Some(f);
    }
    value.extract::<String>().ok()?.parse::<f64>().ok()
}

/// Convert a Python filter value to JSON for comparison against record fields.
/// Returns None for values no record field could ever equal (e.g. sets,
/// arbitrary objects), which the caller treats as "matches nothing".
fn py_to_json(value: &Bound<'_, PyAny>) -> Option<Value> {
    if value.is_none() {
        return Some(Value::Null);
    }
    if let Ok(b) = value.cast::<PyBool>() {
        return Some(Value::Bool(b.is_true()));
    }
    if let Ok(i) = value.extract::<i64>() {
        return Some(Value::from(i));
    }
    if let Ok(f) = value.extract::<f64>() {
        return Some(Value::from(f));
    }
    if let Ok(s) = value.extract::<String>() {
        return Some(Value::String(s));
    }
    if let Ok(list) = value.cast::<PyList>() {
        let mut arr = Vec::with_capacity(list.len());
        for item in list.iter() {
            arr.push(py_to_json(&item)?);
        }
        return Some(Value::Array(arr));
    }
    None
}

#[pyfunction]
#[pyo3(signature = (zipcode, zips=None))]
fn matching<'py>(
    py: Python<'py>,
    zipcode: &str,
    zips: Option<Bound<'py, PyList>>,
) -> PyResult<Bound<'py, PyList>> {
    match zips {
        None => {
            let found = zipcodes::matching(zipcode, None).map_err(to_py_err)?;
            to_pylist(py, &found)
        }
        Some(zips) => {
            let zipcode = zipcodes::clean_zipcode(zipcode).map_err(to_py_err)?;
            filter_pylist(py, &zips, |item| {
                get_str(item, "zip_code").as_deref() == Some(zipcode)
            })
        }
    }
}

#[pyfunction]
fn is_real(zipcode: &str) -> PyResult<bool> {
    zipcodes::is_real(zipcode).map_err(to_py_err)
}

#[pyfunction]
#[pyo3(signature = (prefix, zips=None))]
fn similar_to<'py>(
    py: Python<'py>,
    prefix: &str,
    zips: Option<Bound<'py, PyList>>,
) -> PyResult<Bound<'py, PyList>> {
    let prefix = zipcodes::clean_prefix(prefix).map_err(to_py_err)?;
    match zips {
        None => to_pylist(py, &zipcodes::similar_to(prefix, None)),
        Some(zips) => filter_pylist(py, &zips, |item| {
            get_str(item, "zip_code").is_some_and(|zc| zc.starts_with(prefix))
        }),
    }
}

#[pyfunction]
#[pyo3(signature = (fragment, zips=None))]
fn contains<'py>(
    py: Python<'py>,
    fragment: &str,
    zips: Option<Bound<'py, PyList>>,
) -> PyResult<Bound<'py, PyList>> {
    let fragment = zipcodes::clean_prefix(fragment).map_err(to_py_err)?;
    match zips {
        None => to_pylist(py, &zipcodes::contains(fragment, None)),
        Some(zips) => filter_pylist(py, &zips, |item| {
            get_str(item, "zip_code").is_some_and(|zc| zc.contains(fragment))
        }),
    }
}

#[pyfunction]
#[pyo3(signature = (zips=None, **kwargs))]
fn filter_by<'py>(
    py: Python<'py>,
    zips: Option<Bound<'py, PyList>>,
    kwargs: Option<&Bound<'py, PyDict>>,
) -> PyResult<Bound<'py, PyList>> {
    let mut filters = Vec::new();
    if let Some(kwargs) = kwargs {
        for (key, value) in kwargs.iter() {
            let key: String = key.extract()?;
            match py_to_json(&value) {
                Some(value) => filters.push((key, value)),
                // A value of an inconvertible type can never equal a record
                // field, and all filters must match.
                None => return Ok(PyList::empty(py)),
            }
        }
    }
    match zips {
        None => to_pylist(py, &zipcodes::filter_by_fields(&filters, None)),
        // Both sides of the comparison go through `py_to_json`, never Python
        // rich comparison, so e.g. `active=1` does not match a True field.
        Some(zips) => filter_pylist(py, &zips, |item| {
            filters.iter().all(|(key, value)| {
                item.get_item(key.as_str())
                    .ok()
                    .and_then(|v| py_to_json(&v))
                    .as_ref()
                    == Some(value)
            })
        }),
    }
}

#[pyfunction]
#[pyo3(signature = (lat, long, radius_in_miles, zips=None))]
fn filter_by_coordinates<'py>(
    py: Python<'py>,
    lat: f64,
    long: f64,
    radius_in_miles: f64,
    zips: Option<Bound<'py, PyList>>,
) -> PyResult<Bound<'py, PyList>> {
    match zips {
        None => to_pylist(
            py,
            &zipcodes::filter_by_coordinates(lat, long, radius_in_miles, None),
        ),
        Some(zips) => filter_pylist(py, &zips, |item| {
            match (get_coordinate(item, "lat"), get_coordinate(item, "long")) {
                (Some(z_lat), Some(z_long)) => {
                    zipcodes::haversine(z_long, z_lat, long, lat) <= radius_in_miles
                }
                _ => false,
            }
        }),
    }
}

#[pyfunction]
fn haversine(lon1: f64, lat1: f64, lon2: f64, lat2: f64) -> f64 {
    zipcodes::haversine(lon1, lat1, lon2, lat2)
}

#[pyfunction]
fn list_all<'py>(py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
    to_pylist(py, zipcodes::database())
}

#[pymodule]
fn _zipcodes(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add("FIELD_ORDER", zipcodes::FIELD_ORDER.to_vec())?;
    m.add_function(wrap_pyfunction!(matching, m)?)?;
    m.add_function(wrap_pyfunction!(is_real, m)?)?;
    m.add_function(wrap_pyfunction!(similar_to, m)?)?;
    m.add_function(wrap_pyfunction!(contains, m)?)?;
    m.add_function(wrap_pyfunction!(filter_by, m)?)?;
    m.add_function(wrap_pyfunction!(filter_by_coordinates, m)?)?;
    m.add_function(wrap_pyfunction!(haversine, m)?)?;
    m.add_function(wrap_pyfunction!(list_all, m)?)?;
    Ok(())
}
