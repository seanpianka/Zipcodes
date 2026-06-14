//! Emit the canonical record schema as JSON for the data pipeline to consume.
//!
//! `scripts/update_zipcode_dataset.py` loads `field_order` from the generated
//! file instead of hard-coding it, and CI diffs the committed copy against fresh
//! output so a struct/`FIELD_ORDER` change can't ship without refreshing it.
//!
//! Regenerate with:
//!   cargo run -p zipcodes --example gen_schema > scripts/data/schema.json
fn main() {
    let schema = serde_json::json!({ "field_order": zipcodes::FIELD_ORDER });
    println!("{}", serde_json::to_string_pretty(&schema).unwrap());
}
