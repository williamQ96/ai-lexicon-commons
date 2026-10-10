# Plale Lab Shared Glossary and Operational Definitions

This is a living glossary developed for clearer communication and productivity within Plale Lab and the wider community. It is a public collaborative project, updated over time.

AI research and especially rapidly evolving AI engineering terminology can have blurred boundaries, competing meanings, and meanings that change across time or communities. Those differences can create avoidable communication costs. Readers are assumed to have academic and engineering experience; the aim is to clarify ambiguity rather than provide comprehensive introductory instruction.

**Working proposal; pending team confirmation.** This draft chooses explicit working meanings without claiming lab ratification. A merged pull request or passing build alone does not establish adoption.

[![Build handbook](https://github.com/williamQ96/plale-lab-glossary/actions/workflows/build-pdf.yml/badge.svg)](https://github.com/williamQ96/plale-lab-glossary/actions/workflows/build-pdf.yml)

## Read

- [Searchable handbook and alphabetical index](https://williamq96.github.io/plale-lab-glossary/)
- [Current compiled PDF](https://williamq96.github.io/plale-lab-glossary/glossary.pdf) and [current build record](https://williamq96.github.io/plale-lab-glossary/build-record.html)
- [Archived starter PDF preview](docs/glossary.pdf) and [its snapshot provenance](docs/PDF-SNAPSHOT.md)
- [Shared content source](data/handbook.json)
- [Contribution guide](CONTRIBUTING.md) and [definition-entry template](templates/definition-entry.json)

Each term has its own linked page with a concise definition, scope, inclusions/exclusions, ambiguities, operational criteria, versioned sources, and related terms. The index searches titles, aliases, definitions, boundaries, and sources. Search runs in the browser and sends no queries to a server.

## Source policy

Prefer applicable standards, disciplinary consensus, and authoritative definitions; then peer-reviewed literature, recognizing that peer review alone does not establish consensus. Newer terms may use attributed preprints, first-party technical documentation, and established engineering practices.

Where sources or communities disagree, retain attribution and state this project's chosen working definition. All initial entries remain proposed and pending team confirmation. Source records identify versions or dates and relevant locators.

## One content source, two reading formats

`data/handbook.json` is the single source of truth for the front matter, source policy, references, and term entries. The standard-library Python generator produces the linked website, `main.tex`, and `references.bib` from that JSON.

To edit in GitHub or locally:

1. Edit only `data/handbook.json` for prose, sources, or definitions. Set the content/entry versions and revision dates as appropriate.
2. Commit the JSON to a branch and open a pull request. Actions regenerates the pages and TeX, compiles the PDF, validates shared-source hashes and PDF provenance, and uploads a review artifact.
3. Review the artifact's HTML and PDF. After merge to `main`, a successful build publishes the fresh website and PDF together at the links above. Direct pushes to `main` follow the same build-and-publish flow.

No local TeX installation or generated-file commits are required. Do not hand-edit generated prose. The checked-in HTML, TeX, bibliography, and PDF are starter snapshots for repository browsing; live Pages and run artifacts are the current generated editions. A failed build leaves the previous successful publication available, so check Actions and the site's build record when verifying an update.

For an optional local preview, install Python 3, TeX Live, BibTeX, and latexmk:

```sh
python3 scripts/generate.py
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build -pdflatex="pdflatex -no-shell-escape %O %S" main.tex
python3 scripts/generate.py --snapshot
python3 scripts/generate.py --check
```

On Ubuntu, the TeX packages are `latexmk texlive-latex-base texlive-latex-recommended texlive-fonts-recommended lmodern`. Open `docs/index.html` and `docs/glossary.pdf` locally to review; commit the JSON source change rather than local build output.

## GitHub, TeX, and automatic publication

GitHub displays TeX source and can preview a committed PDF; it does not provide Overleaf's live TeX editor. This project's Actions workflow provides automatic compilation and publication after commits.

The build job runs on pushes, pull requests, and manual runs with only `contents: read`. It uses SHA-pinned official actions, Ubuntu registry-installed TeX, and disabled shell escape. Pull-request builds have no deployment or write permissions and do not publish.

A separate job runs only for this repository's `main` branch, after the build succeeds. It has only `pages: write` and `id-token: write` and publishes the validated Pages artifact. It checks out no repository code, uses no stored credentials, and cannot write commits. Pages uses the **GitHub Actions** source, rather than branch-folder publishing.

For a build artifact, open **Actions → Build handbook → a successful run → Artifacts**, download `handbook-<commit>`, and open `glossary.pdf`. Sign-in and repository read access are required; review artifacts are retained for 30 days. A pull-request run normally compiles the proposed merge commit.

The live site's footer links its source commit and readable PDF build record. The HTML record and its machine-readable JSON companion includes the full commit, run URL, shared-content hash, and PDF checksum; the compiled PDF also records its commit and run. See [hosting details](docs/PAGES.md).

## Contribute and reuse

Submit public sources and synthetic examples. Do not include private chats, unpublished results, datasets, credentials, internal notes, or personal paths. New entries are proposed; adopted status requires an explicit team decision date and public link.

Original handbook prose uses **CC BY 4.0**; build scripts and site code use **MIT**. Third-party sources retain their own rights. See [license scope](LICENSE.md).

[GitHub PDF rendering documentation](https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files#rendering-pdf-documents) · [Artifact downloads](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts)
