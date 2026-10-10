# Initial PDF snapshot

[glossary.pdf](glossary.pdf) is a three-page initial snapshot of the proposed glossary. It is not lab-approved and is not automatically updated by later builds.

- Source commit: [224d5b06667f3711e361e585af239e040abc06c3](https://github.com/williamQ96/plale-lab-glossary/commit/224d5b06667f3711e361e585af239e040abc06c3)
- Successful compilation: [Actions run 38027551153](https://github.com/williamQ96/plale-lab-glossary/actions/runs/38027551153)
- Built PDF: 187,636 bytes; three pages.
- PDF SHA-256: `964487cb0cf671513eede053059524dab5be809707aba36f2fef859bd75fed8b`
- Build environment: Ubuntu 24.04 runner, TeX Live and latexmk from Ubuntu's package registry; TeX shell escape disabled.

The document sources (`main.tex` and `references.bib`) remain the same when this snapshot is committed. The bootstrap export step used to retrieve these public PDF bytes is removed from the ongoing build workflow.

For current content, use the PDF artifact from a successful run for the exact commit you want to read. Future snapshot updates should replace the PDF and update this provenance record together, after compilation and visual review.
