//! Native module `zipcodes._zipcodes`.
//!
//! The Python-facing compat layer (validation, exact 1.x exception messages,
//! `zips=` chaining over caller-supplied dicts) lives in
//! `python/zipcodes/__init__.py`; this module only handles scans over the
//! embedded database, materializing matching records as Python dicts.

use pyo3::prelude::*;
use pyo3::types::{PyBool, PyDict, PyList};
use serde_json::Value;
use zipcodes::Zipcode;

/// Build a dict with the same field order the 1.x pure-Python package produced.
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

fn collect<'py, F>(py: Python<'py>, predicate: F) -> PyResult<Bound<'py, PyList>>
where
    F: Fn(&Zipcode) -> bool,
{
    let dicts = zipcodes::database()
        .iter()
        .filter(|z| predicate(z))
        .map(|z| to_dict(py, z))
        .collect::<PyResult<Vec<_>>>()?;
    PyList::new(py, dicts)
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

/// `zipcode` arrives pre-validated by the Python shim (digits only, length <= 5).
#[pyfunction]
fn matching<'py>(py: Python<'py>, zipcode: &str) -> PyResult<Bound<'py, PyList>> {
    collect(py, |z| z.zip_code == zipcode)
}

#[pyfunction]
fn is_real(zipcode: &str) -> bool {
    zipcodes::database().iter().any(|z| z.zip_code == zipcode)
}

#[pyfunction]
fn similar_to<'py>(py: Python<'py>, prefix: &str) -> PyResult<Bound<'py, PyList>> {
    collect(py, |z| z.zip_code.starts_with(prefix))
}

#[pyfunction]
fn contains<'py>(py: Python<'py>, fragment: &str) -> PyResult<Bound<'py, PyList>> {
    collect(py, |z| z.zip_code.contains(fragment))
}

#[pyfunction]
#[pyo3(signature = (**kwargs))]
fn filter_by<'py>(
    py: Python<'py>,
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
    let filters = filters; // freeze for the closure
    collect(py, |z| filters.iter().all(|(k, v)| z.field_matches(k, v)))
}

#[pyfunction]
fn filter_by_coordinates<'py>(
    py: Python<'py>,
    lat: f64,
    long: f64,
    radius_in_miles: f64,
) -> PyResult<Bound<'py, PyList>> {
    collect(py, |z| {
        match (z.lat.parse::<f64>(), z.long.parse::<f64>()) {
            (Ok(z_lat), Ok(z_long)) => {
                zipcodes::haversine(z_long, z_lat, long, lat) <= radius_in_miles
            }
            _ => false,
        }
    })
}

#[pyfunction]
fn haversine(lon1: f64, lat1: f64, lon2: f64, lat2: f64) -> f64 {
    zipcodes::haversine(lon1, lat1, lon2, lat2)
}

#[pyfunction]
fn list_all<'py>(py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
    collect(py, |_| true)
}

#[pymodule]
fn _zipcodes(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
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
