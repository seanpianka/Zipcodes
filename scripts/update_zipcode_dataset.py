"""Rebuild the embedded zipcode database from the committed base CSV plus
freshly downloaded USPS and GeoNames data.

This is the automated counterpart to ``build_zipcode_dataset.py`` (the legacy
manual pipeline). It is a pure function of its inputs and produces
byte-identical output for identical inputs, so a no-change month yields an
unchanged ``zips.json.bz2``.

Pipeline:
  1. Load the rich base CSV (unitedstateszipcodes.org, committed in-repo —
     its bot protection prevents downloading it from CI).
  2. Apply the legacy zip-codes.com GPS overlay (committed in-repo).
  3. Refresh coordinates from GeoNames where its accuracy is high.
  4. Add any ZIP present in the USPS ZIP Locale Detail file but absent from
     the base, with best-effort field population (issue #23).
  5. Validate, diff against the previous database, compress, write.

Usage:
  python scripts/update_zipcode_dataset.py \
    --base scripts/data/zip_code_database.csv \
    --gps scripts/data/zip-codes-database-FREE.csv \
    --geonames-zip /tmp/geonames_us.zip \
    --usps-xls /tmp/usps_zip_locale.xls \
    --output-bz2 crates/zipcodes/src/zips.json.bz2 \
    --summary-output /tmp/change_summary.json

Requires: xlrd (the USPS file is the legacy binary .xls format).
"""

import argparse
import bz2
import csv
import json
import math
import sys
import zipfile

import xlrd

# Canonical key order of records in zips.json (matches the historical output
# of build_zipcode_dataset.py, which followed the base CSV's column order).
FIELD_ORDER = [
    "zip_code",
    "zip_code_type",
    "active",
    "city",
    "acceptable_cities",
    "unacceptable_cities",
    "state",
    "county",
    "timezone",
    "area_codes",
    "world_region",
    "country",
    "lat",
    "long",
]

# Base CSV column -> public field name, with optional value transform.
SCHEMA = {
    "zip": {"public": "zip_code"},
    "type": {"public": "zip_code_type"},
    "decommissioned": {"public": "active", "transform": lambda v: not bool(int(v))},
    "primary_city": {"public": "city"},
    "acceptable_cities": {"public": "acceptable_cities", "transform": lambda v: split_by_comma(v)},
    "unacceptable_cities": {"public": "unacceptable_cities", "transform": lambda v: split_by_comma(v)},
    "state": {"public": "state"},
    "county": {"public": "county"},
    "timezone": {"public": "timezone"},
    "area_codes": {"public": "area_codes", "transform": lambda v: split_by_comma(v)},
    "world_region": {"public": "world_region"},
    "country": {"public": "country"},
    "latitude": {"public": "lat"},
    "longitude": {"public": "long"},
}

# County-equivalent names from GeoNames that must not get " County" appended.
COUNTY_SUFFIXES = ("county", "parish", "borough", "census area", "municipality", "municipio", "city", "island")

# USPS sheets to scan for ZIPs, in priority order, with the column holding the
# ZIP and the zip_code_type to assign to records synthesized from that sheet.
USPS_SHEETS = [
    ("ZIP_DETAIL", "DELIVERY ZIPCODE", "STANDARD"),
    ("Unique_ZIP_DETAIL", "ZIP CODE", "UNIQUE"),
    ("Other", "ZIP CODE", "PO BOX"),
]

MILITARY_LOCALES = {"APO", "DPO", "FPO"}

MIN_GEONAMES_ROWS = 40_000
MIN_USPS_ZIPS = 30_000
MAX_COUNT_DRIFT = 0.05
SAMPLE_LIMIT = 10


def split_by_comma(s):
    return [i.strip() for i in s.split(",") if i]


def parse_csv(filename):
    with open(filename) as f:
        return [dict(row) for row in csv.DictReader(f, skipinitialspace=True)]


def fmt_coord(value):
    """Normalize a coordinate to at most 4 decimals without trailing zeros."""
    return f"{float(value):.4f}".rstrip("0").rstrip(".")


def load_base(path):
    records = []
    for row in parse_csv(path):
        record = {}
        for key, value in row.items():
            spec = SCHEMA.get(key)
            if spec is None:
                continue
            record[spec["public"]] = spec["transform"](value) if "transform" in spec else value
        records.append(record)
    return records


def apply_legacy_gps_overlay(records, gps_csv_path):
    """Overlay the committed zip-codes.com coordinates (legacy behavior)."""
    by_zip = {r["zip_code"]: r for r in records}
    for place in parse_csv(gps_csv_path):
        record = by_zip.get(place["ZipCode"])
        if record is not None:
            record["lat"] = place["Latitude"]
            record["long"] = place["Longitude"]


def load_geonames(zip_path):
    """Parse GeoNames US.zip -> {zip: {place, county, lat, long, accuracy}}."""
    with zipfile.ZipFile(zip_path) as z:
        lines = z.open("US.txt").read().decode("utf-8").splitlines()
    if len(lines) < MIN_GEONAMES_ROWS:
        sys.exit(f"FATAL: GeoNames file has only {len(lines)} rows (>= {MIN_GEONAMES_ROWS} expected); truncated download?")
    geo = {}
    for line in lines:
        cols = line.split("\t")
        zip_code = cols[1]
        if zip_code in geo:
            continue
        geo[zip_code] = {
            "place": cols[2],
            "county": cols[5],
            "lat": cols[9],
            "long": cols[10],
            "accuracy": int(cols[11]) if cols[11].isdigit() else 0,
        }
    return geo


def load_usps(xls_path):
    """Parse the USPS ZIP Locale Detail .xls -> {zip: {city, state, type}}."""
    book = xlrd.open_workbook(xls_path)
    usps = {}
    for sheet_name, zip_column, zip_type in USPS_SHEETS:
        sheet = book.sheet_by_name(sheet_name)
        header = [str(sheet.cell_value(0, c)).strip() for c in range(sheet.ncols)]
        zip_idx = header.index(zip_column)
        locale_idx = header.index("LOCALE NAME")
        state_idx = header.index("PHYSICAL STATE")
        for r in range(1, sheet.nrows):
            zip_code = str(sheet.cell_value(r, zip_idx)).strip()
            if zip_code not in usps:
                usps[zip_code] = {
                    "city": str(sheet.cell_value(r, locale_idx)).strip(),
                    "state": str(sheet.cell_value(r, state_idx)).strip(),
                    "type": zip_type,
                }
    if len(usps) < MIN_USPS_ZIPS:
        sys.exit(f"FATAL: USPS file yielded only {len(usps)} ZIPs (>= {MIN_USPS_ZIPS} expected); corrupt download?")
    return usps


def refresh_coordinates(records, geo):
    """Overwrite lat/long with GeoNames values where its accuracy is high.

    GeoNames accuracy 4+ means the coordinate is tied to a resolved place
    rather than estimated; lower-accuracy entries keep the legacy value.
    """
    for record in records:
        entry = geo.get(record["zip_code"])
        if entry and entry["accuracy"] >= 4:
            record["lat"] = fmt_coord(entry["lat"])
            record["long"] = fmt_coord(entry["long"])


def military_state(zip_code):
    """Armed-forces 'state' for a military ZIP prefix, or None."""
    prefix = int(zip_code[:3])
    if 90 <= prefix <= 98:
        return "AE"
    if prefix == 340:
        return "AA"
    if 962 <= prefix <= 966:
        return "AP"
    return None


def haversine_miles(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    a = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 3956 * math.asin(math.sqrt(a))


def build_timezone_lookups(records):
    """Coordinates of every zoned record, plus each state's modal timezone."""
    points = []
    by_state = {}
    for record in records:
        if not record["timezone"]:
            continue
        by_state.setdefault(record["state"], {}).setdefault(record["timezone"], 0)
        by_state[record["state"]][record["timezone"]] += 1
        try:
            lat, long = float(record["lat"]), float(record["long"])
        except ValueError:
            continue
        if lat or long:
            points.append((lat, long, record["timezone"]))
    modal = {
        state: max(sorted(counts), key=lambda tz: counts[tz])
        for state, counts in by_state.items()
    }
    return points, modal


def nearest_timezone(lat, long, points):
    return min(points, key=lambda p: haversine_miles(lat, long, p[0], p[1]))[2]


def synthesize_record(zip_code, usps_entry, geo, tz_points, tz_modal):
    """Best-effort record for a ZIP known to USPS but absent from the base."""
    city = usps_entry["city"].title()
    mil_state = military_state(zip_code)
    if mil_state is not None and usps_entry["city"].upper() in MILITARY_LOCALES:
        return {
            "zip_code": zip_code,
            "zip_code_type": "MILITARY",
            "active": True,
            "city": city,
            "acceptable_cities": [],
            "unacceptable_cities": [],
            "state": mil_state,
            "county": "",
            "timezone": "",
            "area_codes": [],
            "world_region": "NA",
            "country": "US",
            "lat": "0",
            "long": "0",
        }

    entry = geo.get(zip_code)
    county, lat, long = "", "0", "0"
    if entry:
        county = entry["county"]
        if county and not county.lower().endswith(COUNTY_SUFFIXES):
            county += " County"
        if entry["accuracy"] >= 1:
            lat, long = fmt_coord(entry["lat"]), fmt_coord(entry["long"])
    if lat != "0" or long != "0":
        timezone = nearest_timezone(float(lat), float(long), tz_points)
    else:
        timezone = tz_modal.get(usps_entry["state"], "")
    return {
        "zip_code": zip_code,
        "zip_code_type": usps_entry["type"],
        "active": True,
        "city": city,
        "acceptable_cities": [],
        "unacceptable_cities": [],
        "state": usps_entry["state"],
        "county": county,
        "timezone": timezone,
        "area_codes": [],
        "world_region": "NA",
        "country": "US",
        "lat": lat,
        "long": long,
    }


def fill_missing(records, usps, geo, mark_decommissioned):
    known_states = {r["state"] for r in records}
    existing = {r["zip_code"] for r in records}
    tz_points, tz_modal = build_timezone_lookups(records)

    added = []
    for zip_code in sorted(set(usps) - existing):
        entry = usps[zip_code]
        if len(zip_code) != 5 or not zip_code.isdigit():
            print(f"skipping USPS ZIP with invalid format: {zip_code!r}")
            continue
        if entry["state"] not in known_states and military_state(zip_code) is None:
            print(f"skipping USPS ZIP {zip_code} with unknown state {entry['state']!r} (locale: {entry['city']!r})")
            continue
        added.append(synthesize_record(zip_code, entry, geo, tz_points, tz_modal))
    records.extend(added)

    if mark_decommissioned:
        for record in records:
            if record["active"] and record["zip_code"] not in usps:
                record["active"] = False


def canonicalize(records):
    records.sort(key=lambda r: r["zip_code"])
    return [{field: r[field] for field in FIELD_ORDER} for r in records]


def load_previous(bz2_path):
    try:
        with open(bz2_path, "rb") as f:
            return json.loads(bz2.decompress(f.read()))
    except FileNotFoundError:
        return []


def validate(records, previous):
    failures = []
    if previous:
        drift = abs(len(records) - len(previous)) / len(previous)
        if drift > MAX_COUNT_DRIFT:
            failures.append(
                f"record count changed by {drift:.1%} ({len(previous)} -> {len(records)}); exceeds {MAX_COUNT_DRIFT:.0%} safety threshold"
            )
    zips = [r["zip_code"] for r in records]
    if len(set(zips)) != len(zips):
        failures.append("duplicate zip_code values present")
    if zips != sorted(zips):
        failures.append("records are not sorted by zip_code")
    for record in records:
        if list(record) != FIELD_ORDER:
            failures.append(f"record {record.get('zip_code')!r} has wrong fields: {list(record)}")
            break
        if not isinstance(record["active"], bool):
            failures.append(f"record {record['zip_code']} has non-bool 'active'")
            break
        if any(not isinstance(record[f], list) for f in ("acceptable_cities", "unacceptable_cities", "area_codes")):
            failures.append(f"record {record['zip_code']} has a non-list list-field")
            break
    return failures


def compute_summary(previous, current):
    old_by_zip = {r["zip_code"]: r for r in previous}
    new_by_zip = {r["zip_code"]: r for r in current}
    added = sorted(set(new_by_zip) - set(old_by_zip))
    removed = sorted(set(old_by_zip) - set(new_by_zip))
    modified = []
    for zip_code in sorted(set(old_by_zip) & set(new_by_zip)):
        old, new = old_by_zip[zip_code], new_by_zip[zip_code]
        changes = {f: [old[f], new[f]] for f in FIELD_ORDER if old[f] != new[f]}
        if changes:
            modified.append({"zip_code": zip_code, "changes": changes})
    return {
        "total_before": len(previous),
        "total_after": len(current),
        "added_count": len(added),
        "removed_count": len(removed),
        "modified_count": len(modified),
        "added_sample": [new_by_zip[z] for z in added[:SAMPLE_LIMIT]],
        "removed_sample": [old_by_zip[z] for z in removed[:SAMPLE_LIMIT]],
        "modified_sample": modified[:SAMPLE_LIMIT],
    }


def write_output(records, bz2_path):
    payload = json.dumps(records).encode("utf-8")
    compressed = bz2.compress(payload, compresslevel=9)
    with open(bz2_path, "wb") as f:
        f.write(compressed)
    # Round-trip the file we just wrote to prove it is loadable.
    if json.loads(bz2.decompress(compressed)) != records:
        sys.exit("FATAL: bz2 round-trip mismatch")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", required=True, help="committed unitedstateszipcodes.org CSV")
    parser.add_argument("--gps", default="scripts/data/zip-codes-database-FREE.csv", help="committed zip-codes.com GPS overlay CSV")
    parser.add_argument("--geonames-zip", required=True, help="GeoNames US.zip (download.geonames.org/export/zip/US.zip)")
    parser.add_argument("--usps-xls", required=True, help="USPS ZIP Locale Detail .xls (postalpro.usps.com/ZIP_Locale_Detail)")
    parser.add_argument("--output-bz2", required=True, help="path of the embedded database to diff against and overwrite")
    parser.add_argument("--summary-output", required=True, help="where to write the JSON change summary")
    parser.add_argument(
        "--mark-decommissioned",
        action="store_true",
        help="set active=false on ZIPs absent from the USPS list (off by default)",
    )
    args = parser.parse_args()

    previous = load_previous(args.output_bz2)
    geo = load_geonames(args.geonames_zip)
    usps = load_usps(args.usps_xls)

    records = load_base(args.base)
    print(f"base records: {len(records)}")
    apply_legacy_gps_overlay(records, args.gps)
    refresh_coordinates(records, geo)
    fill_missing(records, usps, geo, args.mark_decommissioned)
    records = canonicalize(records)

    failures = validate(records, previous)
    if failures:
        for failure in failures:
            print(f"VALIDATION FAILED: {failure}", file=sys.stderr)
        sys.exit(1)

    summary = compute_summary(previous, records)
    with open(args.summary_output, "w") as f:
        json.dump(summary, f, indent=2)
    write_output(records, args.output_bz2)
    print(
        f"records: {summary['total_before']} -> {summary['total_after']} "
        f"(+{summary['added_count']} / -{summary['removed_count']} / ~{summary['modified_count']} modified)"
    )


if __name__ == "__main__":
    main()
