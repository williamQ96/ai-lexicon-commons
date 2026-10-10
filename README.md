# Plale Lab Shared Glossary and Operational Definitions

This is a living glossary developed for clearer communication and productivity within Plale Lab and the wider community. It is a public collaborative project, updated over time.

AI research and especially rapidly evolving AI engineering terminology can have blurred boundaries, competing meanings, and meanings that change across time or communities. Those differences can create avoidable communication costs. Readers are assumed to have academic and engineering experience; the aim is to clarify ambiguity rather than provide comprehensive introductory instruction.

**Working proposal; pending team confirmation.** This draft chooses explicit working meanings without claiming lab ratification. A merged pull request or passing build alone does not establish adoption.

[![Build handbook](https://github.com/williamQ96/plale-lab-glossary/actions/workflows/build-pdf.yml/badge.svg)](https://github.com/williamQ96/plale-lab-glossary/actions/workflows/build-pdf.yml)

## Read

- [Searchable handbook and alphabetical index](https://williamq96.github.io/plale-lab-glossary/)
- [Compiled PDF preview](docs/glossary.pdf) and [snapshot provenance](docs/PDF-SNAPSHOT.md)
- [Shared content source](data/handbook.json)
- [Contribution guide](CONTRIBUTING.md) and [definition-entry template](templates/definition-entry.json)

Each term has its own linked page with a concise definition, scope, inclusions/exclusions, ambiguities, operational criteria, versioned sources, and related terms. The index searches titles, aliases, definitions, boundaries, and sources. Search runs in the browser and sends no queries to a server.

## Source policy

Prefer applicable standards, disciplinary consensus, and authoritative definitions; then peer-reviewed literature, recognizing that peer review alone does not establish consensus. Newer terms may use attributed preprints, first-party technical documentation, and established engineering practices.

Where sources or communities disagree, retain attribution and state this project's chosen working definition. All initial entries remain proposed and pending team confirmation. Source records identify versions or dates and relevant locators.

## One content source, two reading formats

`data/handbook.json` holds the front matter, source policy, source records, and terms. The standard-library Python generator produces `main.tex`, `references.bib`, the index, and all term pages. Do not hand-edit generated prose. CI checks these outputs and the PDF snapshot's source hash to detect drift.

To regenerate, install Python 3, TeX Live, BibTeX, and latexmk:

```sh
python3 scripts/generate.py
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build -pdflatex="pdflatex -no-shell-escape %O %S" main.tex
python3 scripts/generate.py --snapshot
python3 scripts/generate.py --check
```

On Ubuntu, the TeX packages are `latexmk texlive-latex-base texlive-latex-recommended texlive-fonts-recommended lmodern`. The snapshot command copies the compiled PDF into `docs/` and records its content and PDF hashes. Review the website and PDF, then commit the JSON and generated outputs together.

## GitHub and TeX

GitHub displays TeX source and can preview a committed PDF; it does not provide Overleaf's live TeX editor. Actions validates and compiles on pushes and pull requests using SHA-pinned official actions, Ubuntu registry-installed TeX, disabled shell escape, and only `contents: read` permission.

For a fresh build, open **Actions → Build handbook → a successful run → Artifacts**, download `handbook-<commit>`, and open `glossary.pdf`. Sign-in and repository read access are required; artifacts are retained for 30 days. A pull-request run normally compiles the proposed merge commit.

The public site serves the checked-in `docs/` tree. PDF/site updates are included in source commits; the compilation workflow has no deployment or repository-write permissions.

## Contribute and reuse

Submit public sources and synthetic examples. Do not include private chats, unpublished results, datasets, credentials, internal notes, or personal paths. New entries are proposed; adopted status requires an explicit team decision date and public link.

Original handbook prose uses **CC BY 4.0**; build scripts and site code use **MIT**. Third-party sources retain their own rights. See [license scope](LICENSE.md).

[GitHub PDF rendering documentation](https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files#rendering-pdf-documents) · [Artifact downloads](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts)
