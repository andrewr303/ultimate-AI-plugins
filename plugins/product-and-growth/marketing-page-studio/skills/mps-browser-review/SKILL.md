---
name: mps-browser-review
description: "Use when reviewing and repairing the actual browser rendering, interactions, responsiveness, accessibility, performance or reduced-motion behavior of a product marketing site."
---

# Browser critique and repair

Read [website QA](../../references/website-qa.md). Run `python scripts/studio.py web verify --site SITE --output REPORTS` for the bundled fixture-compatible checks. For a different app, adapt tests to its selectors and workflows; a fixture pass is not a pass for a client site.

1. Confirm the tested source hash/revision, route, viewport and motion preference. Capture initial, active, result and recovery states rather than only the hero.
2. Test 390, 768, 1024 and 1440px representative widths; inspect mobile hierarchy and horizontal overflow. Add the product's specified widths when relevant.
3. Operate tabs/forms/filter/reorder/edit/details/replay with keyboard and pointer. Verify loading, success, empty/error, retry, cancel/reset and focus recovery. Scroll forward and backward.
4. Inspect reduced motion, semantic order, contrast, labels, status announcements, focus visibility and target sizes. Test with JavaScript disabled for intended low-JS pages.
5. Record browser console/page/network errors, layout shifts, reserved asset sizes and offscreen activity. Check native image detail and product text at actual display size.
6. Separate mechanical failures from design critique. Identify the most consequential defect, repair its cause and rerun the affected observations. Keep old evidence only as comparison.

Report exactly which checks ran and what remains untested, including screen-reader/device coverage. A clean console cannot establish that a page is persuasive or beautiful.
