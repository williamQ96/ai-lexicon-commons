# Plale Lab Shared Glossary and Operational Definitions

**Working proposal for team review — not lab-approved.** This starter offers a format and illustrative definitions for discussion. It does not claim team consensus or establish lab policy.

[![Build glossary PDF](https://github.com/williamQ96/plale-lab-glossary/actions/workflows/build-pdf.yml/badge.svg)](https://github.com/williamQ96/plale-lab-glossary/actions/workflows/build-pdf.yml)

## Read and edit

- [Initial PDF preview](docs/glossary.pdf) is a checked-in snapshot; [build provenance](docs/PDF-SNAPSHOT.md) identifies its source commit.
- [TeX source](main.tex) contains the glossary and three illustrative proposed entries.
- [Definition template](templates/definition-entry.tex) provides a copyable entry.
- [Contribution guide](CONTRIBUTING.md) explains how to propose and review changes.
- [Public references](references.bib) records sources and versions.
- [Builds and PDFs](https://github.com/williamQ96/plale-lab-glossary/actions/workflows/build-pdf.yml) lists compilation runs.
- [Optional Pages approach](docs/PAGES.md) describes a future public reading page.

GitHub displays TeX as source; it does not provide Overleaf's live TeX editor and compilation preview. GitHub can preview a committed PDF. This repository compiles the source with GitHub Actions on pushes and pull requests.

For a fresh PDF, open **Actions → Build glossary PDF → a successful run → Artifacts**, select `glossary-pdf-<commit>`, download the archive, and open `main.pdf`. GitHub sign-in and repository read access are required for artifact downloads. Artifacts are retained for 30 days. The checked-in PDF is an initial snapshot and is not automatically refreshed. Match the run's commit to the source you want to read; a pull-request run normally compiles GitHub's proposed merge commit.

## Build locally

Install TeX Live (or an equivalent distribution), BibTeX, and latexmk. Run from the repository root:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build -pdflatex="pdflatex -no-shell-escape %O %S" main.tex
```

The output is `build/main.pdf`. On Ubuntu, the CI dependencies can be installed from the distribution's package registry:

```sh
sudo apt-get update
sudo apt-get install --no-install-recommends latexmk texlive-latex-base texlive-latex-recommended texlive-fonts-recommended lmodern
```

The workflow pins official GitHub actions to commit SHAs, installs TeX through Ubuntu's package registry, disables TeX shell escape, and requests only `contents: read`. It does not deploy a site or write back to the repository.

## Propose a definition

Use one entry per term. Include a working definition, scope, inclusions, exclusions, operational criteria where applicable, source and version, entry version, and proposed/adopted status. New entries start as **proposed**. Mark an entry **adopted** only with a public, explicit team decision and its date/link; merging a pull request alone is not evidence of adoption.

Use public sources and synthetic examples. Do not submit private conversations, unpublished results, datasets, credentials, or internal notes.

## Licensing

No license has been selected. Public visibility does not itself grant a reuse license. The repository owner and team can decide the appropriate license later.

## GitHub reading and build documentation

- [PDF rendering on GitHub](https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files#rendering-pdf-documents)
- [Downloading workflow artifacts](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts)
