# Policy Validator Next Steps Roadmap

This document outlines the enhancements planned for the policy-validator tool to improve semantic consistency checking across planning Markdown files.

## 1. Canonical Reference Override
- Add CLI option `--canonical-section-file` or frontmatter key to mark a canonical file per section.
- Fallback to majority-based canonical only when no override is provided.

## 2. Required-Section Enforcement
- Treat missing required sections as schema errors (exit code 2).
- Support per-file opt-out via frontmatter flag `skip_section_validation: true`.

## 3. Advanced Markdown Normalization
- Strip/standardize internal links, images, code fences, tables, and list markers.
- Normalize heading levels before extraction (allow `##`/`###` equivalence).
- Collapse multiple blank lines.

## 4. Fuzzy and Token-Set Diffing
- Compute similarity scores (e.g., via `difflib.SequenceMatcher`).
- Warn or fail when similarity below configurable threshold (default 90%).

## 5. Configurable Sections and Thresholds
- Move `section_names` and diff thresholds into external YAML or JSON config.
- Allow dynamic addition of new sections without code changes.

## 6. Rich Reporting and Exit Codes
- Return distinct exit codes for:
  - Schema errors (1)
  - Policy conflicts (2)
  - Section conflicts (3)
- Provide HTML or JUnit XML report for CI integration with side-by-side diffs.

## 7. Incremental/Changed-Only Mode
- Add `--since-branch` or `--changed-only` flag to process only files changed since last commit.
- Cache section hashes to speed up repeated runs.

## 8. Git Integration Hooks
- Provide sample pre-commit hook or GitHub Actions workflow for automatic checks on PRs.
- Publish a template action under `.github/workflows/`.

## 9. Performance & Caching
- Introduce in-memory or on-disk cache of parsed frontmatter & normalized sections.
- Add `--clear-cache` flag.

## 10. Testing and Documentation
- Expand unit tests for all new behaviors, including fuzzy thresholds and canonical overrides.
- Update README.md with usage examples and CI integration instructions.

---
Once implemented, commit and push changes to GitHub to activate CI checks.