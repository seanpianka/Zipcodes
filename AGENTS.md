# Working on Zipcodes

Zipcodes publishes one Rust query engine as a Rust crate and a Python package.
Preserve its embedded, lazy-loaded dataset: ordinary queries must work without
SQLite, network access, or external runtime data files.

## Changes across languages

- Keep shared query and validation logic in the Rust core. Python adapters
  preserve Python argument handling, return shapes, and exception behavior.
- Preserve the current public contract unless the task intentionally changes it.
  Check current tests and release notes rather than assuming all historical
  Python behavior still applies.
- For public API changes, explicitly consider the Rust core, PyO3 bindings,
  Python wrapper, tests, and examples. Update affected surfaces and identify
  intentional differences between the languages.
- The root README serves both languages and supplies the PyPI description;
  `crates/zipcodes/README.md` serves Rust users. When changing usage guidance,
  check both audiences. Rust API documentation comes from source comments.

## Data and verification

- Before changing dataset generation, read the README's Zipcode Data section
  and the update workflow. Keep source provenance and generated data consistent.
- Use `.github/workflows/ci.yml` for the current checks and platform matrix.
  Run targeted checks for the changed behavior; binding changes require testing
  a freshly built Python extension so an installed wheel cannot hide regressions.
- For documentation edits, check links, examples, and the diff. Check badge
  contents as well as HTTP success: a valid image can display a provider error.
- Describe statistics using the provider's actual measurement period. If a
  requested metric is unavailable, report the gap rather than relabeling another.

## Working and reporting

- Keep changes scoped to the request and preserve unrelated work. Distinguish
  planning documents from implemented behavior when describing capabilities.
- Before release-related actions, read `release.yml` and `auto-release.yml` in
  `.github/workflows/`: publishing a version tag or merging a data-update PR can
  publish packages. Use the current conversation's authorization for commits,
  pushes, PRs, merges, and releases; account for these downstream effects.
- Report what changed, what was verified, and what remains unresolved concisely.
  Check every requested outcome before claiming completion; a working substitute
  does not by itself satisfy the original requirement.
