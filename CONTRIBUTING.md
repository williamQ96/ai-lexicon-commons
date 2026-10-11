# Contributing to the living glossary

Edit `data/handbook.json`, the single content source for HTML, TeX, the bibliography and the internal guide. For detailed editing rules, use [.agents/skills/plalelab-glossry-edit/SKILL.md](.agents/skills/plalelab-glossry-edit/SKILL.md), its template and schema/content/page references.

1. Keep existing slugs stable. For a new entry, copy `templates/definition-entry.json`, replace its scaffold prose and unresolved source ID, and intentionally add its slug to `display_order`.
2. Research applicable institutional definitions, peer-reviewed papers, industry standards / first-party documents / preprints / academic materials, then Lab proposals, in that order. Verify original versions, status and scope. Record gaps instead of inventing consensus or promoting university-hosted preprints.
3. Every definition, comparison, boundary, operational criterion and relationship condition has nearby source IDs. Mark editorial interpretations. Compare differing usages explicitly and explain applicability.
4. Use is-a only for externally supported subtypes of compatible semantic kinds. Uses and supports/orchestrates are component/control relations. Validate targets and source coverage. Related links do not assert taxonomy.
5. New meanings are proposed with adoption null. Green adopted status requires a real unanimous consensus decision, date, accessible HTTPS record and specific evidence. A merge or publication does not establish adoption. Update versions, dates and revision records.
6. Run `python -m unittest discover -s tests -v` and `python scripts/preview.py --build-only`; inspect desktop, tablet, phone and dark mode. Validate the editing skill when changing its format. Only compile/snapshot a fresh PDF if TeX is available; identify old PDFs by their real edition.

Keep private chats, unpublished results, credentials and personal paths out of public content. Summarize authorized internal proposals in the versioned guide without publishing transcripts. Original prose is CC BY 4.0 and code is MIT; preserve third-party rights.

The skill does not authorize commits, pushes, deployment or external messages. When publication is separately authorized, Actions builds review artifacts on branches/PRs and publishes only successful main-branch builds; see README.md.
