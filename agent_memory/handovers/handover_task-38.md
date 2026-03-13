## Task SUCCESS: Add Pillar-Cluster template + CTA patterns

### Status: SUCCESS

### What Was Done
- Added `PillarClusterArticle` dataclass (headline, pillar_summary, clusters, internal_links, cta)
- Added `CTA_PATTERNS` dict with 3 categories: engagement, conversion, sharing (3 patterns each)
- Extended `format_instructions()` to support "pillar_cluster" format type

### Files Modified
- `src/writing/templates.py` — Added dataclass, CTA_PATTERNS, format instructions
- `tests/unit/test_pillar_cluster.py` — New test file (22 tests)

### Quality Results
- ruff: passed
- mypy: passed
- pytest: 519 passed

### Next Steps
- Task 39: Update humanizer for new architectures
