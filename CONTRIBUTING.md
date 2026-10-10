# Contributing

This is a working proposal for team review. The contribution process below is also proposed.

1. Copy [the TeX entry template](templates/definition-entry.tex) into `main.tex`, or revise one existing entry.
2. State the meaning, scope, inclusions and exclusions. Add operational criteria for measurement or classification; explain "not applicable" or mark unfinished criteria "pending".
3. Record a public source and version/date, or identify an original proposal. Add BibTeX references to `references.bib`.
4. Give the entry a version and revision date. New entries remain **proposed**. Include a synthetic example or counterexample if useful.
5. Open a pull request explaining the term, the ambiguity it addresses, and remaining questions. Review the PDF artifact before merging.

Mark an entry **adopted** only when an explicit team decision is recorded with a date and public link. A merge, review approval, or successful build alone does not establish lab adoption.

Use public material only. Do not include private chats, unpublished results, datasets, credentials, internal notes, or personal file paths. Use fictional examples where needed.

Compile with the command in [README.md](README.md). GitHub Actions must compile successfully; also read the PDF to check formatting and meaning. Build success verifies compilation, not semantic agreement.

Keep generated TeX files in `build/`. If a PDF snapshot is committed, record its source commit and update it only after a successful build.

No license has been assigned. Discuss licensing with the repository owner before adding a license file.
