---
name: open-ai-glossary-edit
description: Research, add or revise Open AI Glossary entries with versioned citations, typed concept relationships, adoption evidence and a quiet English reading layout. Use for glossary content and page edits in Open AI Glossary.
---

# Open AI Glossary editing

Edit the project's `data/handbook.json`, the sole content source for HTML and TeX. Locate the repository from the active workspace; do not assume a machine-specific path. Read the relevant existing entry and [content contract](references/content-contract.md). For a new entry, start from [entry template](assets/definition-entry.json); consult the [JSON schema](references/content-schema.json) for field shapes. Keep independently addressable slugs stable, especially `llm`.

## Research and attribution

Research in this fixed order: applicable **formal institutional definitions**, **peer-reviewed papers**, **industry standards / first-party documentation / preprints / academic materials**, then **Repository internal proposals**. Verify original text, edition/date, publication status and context before writing. Corporate technical blogs belong to tier 3; university hosting does not make a paper an institutional definition. An official draft remains a draft, not a final standard. Record a gap if applicable higher-tier evidence is unavailable. Relevance wins over an unrelated authority; one paper is not consensus.

Write English prose. Every definition, boundary, operational criterion and relationship conclusion uses a cited statement with `text` and nonempty `source_ids` (relations use `condition`). Keep inline citations close to claims. Version each source with a locator, scope, access date and verification note. Document retrieval limitations honestly. Mark derived conclusions `inference: true`; a supporting citation is not the source's endorsement of the inference. Keep distinct meanings attributed in `definition_views`. For paired explanations, use cited comparison cells in one canonical term section and validated `reading_links` from related terms.

Treat the user's terminology guide as a versioned internal proposal in `lab_guide`, rendered at `lab-guide.html`. Summarize authorized proposals; do not publish chat transcripts. Add a tier-4 source referring to its ID and version. Do not silently replace the initial proposal with an editorial revision or imply ratification.

## Relations and adoption

Use only `is-a`, `uses`, `supports/orchestrates`, with a target, condition, source IDs and explicit inference flag. **Strict subtype nesting is reserved for is-a**, between compatible `concept_kind` values and with external support. A component relationship is not a subtype: an LLM-based agent uses an LLM; a harness supports/orchestrates workflows. Preserve competing scopes instead of forcing every term into one chain.

New or unresolved working meanings use `status: proposed`, `adoption: null` and the yellow text tag **Repository · Proposed / not certified**. Green **Repository · Certified by consensus** requires an actual unanimous decision, ISO date, accessible HTTPS decision link and a specific evidence record. Inspect that linked record for the claimed consensus before changing status. A user asking for green, a merged commit, a deployment or an authoritative external source is not adoption evidence. If evidence is absent, keep proposed and explain the missing decision; continue other authorized edits.

## Page and verification

Read [page contract](references/page-contract.md) for the selected B navigation + A reading design. Each entry includes definition, attributed comparison, scope, inclusions and counterexamples, ambiguities, operational criteria, typed relationships, Repository meaning, research gaps, versioned sources and revisions. Optional explanatory images need meaningful explanatory value, caption, alt text and cited relation provenance; never replace prose or evidence with an image.

Update `display_order`, references, related links, source coverage, content/entry versions and revision dates together. Run `python -m unittest discover -s tests -v` and `python scripts/preview.py --build-only`. The semantic validator must reject unknown/missing citations, dangling targets, incompatible or cyclic is-a edges and adopted status without evidence. Inspect desktop, tablet, mobile and dark mode; verify real search, clear, TOC and related links. Without JavaScript, prose and navigation remain readable.

If producing committed generated files, run `python scripts/generate.py`; HTML, TeX and bibliography must consume the same JSON. Compile and snapshot only a genuinely fresh PDF. If TeX is unavailable, clearly label the old PDF's actual edition and preserve its provenance. Never relabel an old PDF as current. Report local preview and changed files. This skill does not independently authorize committing, pushing, deploying or messaging another task.
