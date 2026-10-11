# Quiet reading design

Preserve the selected fusion: B's persistent browser-local search/navigation and A's Newsreader reading typography. Use existing self-hosted Manrope + Newsreader, paper/forest neutral tokens, generous space and thin separators. The surface is a reference for researchers and engineers; do not introduce marketing heroes, decorative cards or new unsupported claims.

Homepage and navigation follow display_order. On desktop, search and catalog are left of a readable column; on mobile the search remains visible and a native details catalog collapses. Detail pages offer a native mobile/tablet in-page directory, a desktop contents column and independent related links. Source citations are compact numbered links to full records. Search includes comparison text, relation conditions/type/target titles, aliases and boundaries.

Use neutral text for external source types. Reserve small yellow/green tags for **internal** adoption, and always spell out their meaning. Colors: light yellow #6b4b00 on #fff0bc, light green #175634 on #e5f1e9; dark yellow #f3d685 on #433719, dark green #c4eccf on #1c3b29. Text contrast must remain at least 4.5:1. Neither green color nor external authority implies Lab consensus.

Show compatible is-a relations as a small nested list; show uses/supports relationships as labeled rows with conditions and citations. No nested agent-under-LLM or harness-under-workflow visualization. Plain prose carries all explanation and evidence. Reference implementation: scripts/web_layout.py, scripts/render.py, docs/assets/style.css and docs/assets/search.js. Update DESIGN.md when a sanctioned design rule changes.

Inspect desktop 1280, tablet 1024, phone 390 widths and dark mode in one batched pass. Test query persistence, empty results, clear/focus, mobile catalog and page directory, source anchors and related routes. Also verify native no-JavaScript reading via generated HTML. Optional images must be additive and stay legible on small screens.

Peripheral reading must remain comfortable: header and page-directory text use 14px, main catalog links 15px, search/metadata/source labels at least 13px (search input 16px on phone). Preserve the larger serif reading hierarchy. Widen the catalog and directory modestly when needed; verify long directory labels and touch targets rather than shrinking text to fit. Paired comparison rows use fine separators; phone layouts stack labeled cells without horizontal scrolling.
