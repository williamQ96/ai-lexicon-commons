# Plale Lab Shared Glossary and Operational Definitions

This is a living glossary developed for clearer communication and productivity within Plale Lab and the wider community. It is a public collaborative project, updated over time.

AI research and especially rapidly evolving AI engineering terminology can have blurred boundaries, competing meanings, and meanings that change across time or communities. Those differences can create avoidable communication costs. Readers are assumed to have academic and engineering experience; the aim is to clarify ambiguity rather than provide comprehensive introductory instruction.

**Working proposal; pending team confirmation.** This draft chooses explicit working meanings without claiming lab ratification. A merged pull request or passing build alone does not establish adoption.

[![Build handbook](https://github.com/williamQ96/plale-lab-glossary/actions/workflows/build-pdf.yml/badge.svg)](https://github.com/williamQ96/plale-lab-glossary/actions/workflows/build-pdf.yml)

## Read

- [Searchable handbook and reading index](https://williamq96.github.io/plale-lab-glossary/)
- [Current compiled PDF](https://williamq96.github.io/plale-lab-glossary/glossary.pdf) and [current build record](https://williamq96.github.io/plale-lab-glossary/build-record.html)
- [Archived starter PDF preview](docs/glossary.pdf) and [its snapshot provenance](docs/PDF-SNAPSHOT.md)
- [Shared content source](data/handbook.json)
- [Contribution guide](CONTRIBUTING.md) and [definition-entry template](templates/definition-entry.json)

Edition 0.6 has six active terms in reading order: Workflow, Harness, Model, LLM, Agent, Schema. Each independent page compares definitions, explains boundaries and operational criteria, shows typed relationships and a cited Lab proposal, and records source gaps and revisions. Search includes aliases, definition comparisons and relationship conditions. Search runs in the browser and sends no queries to a server.

## Source policy

Research applicable formal institutional definitions first, peer-reviewed papers second, industry standards / first-party documentation / preprints / academic materials third, and Lab internal proposals last. Corporate engineering blogs are tier 3. Verify publication status and context; relevance outweighs unrelated authority. Peer review does not alone establish consensus.

Where sources or communities disagree, retain attribution and state this project's chosen working definition. All initial entries remain proposed and pending team confirmation. Source records identify versions or dates and relevant locators.

## One content source, two reading formats

`data/handbook.json` is the single source of truth for the front matter, source policy, references, and term entries. The standard-library Python generator produces the linked website, `main.tex`, and `references.bib` from that JSON.

To edit in GitHub or locally:

1. Edit only `data/handbook.json` for prose, sources, or definitions. Set the content/entry versions and revision dates as appropriate.
2. Commit the JSON to a branch and open a pull request. Actions regenerates the pages and TeX, compiles the PDF, validates shared-source hashes and PDF provenance, and uploads a review artifact.
3. Review the artifact's HTML and PDF. After merge to `main`, a successful build publishes the fresh website and PDF together at the links above. Direct pushes to `main` follow the same build-and-publish flow.

No local TeX installation or generated-file commits are required. Do not hand-edit generated prose. The checked-in HTML, TeX, bibliography, and PDF are starter snapshots for repository browsing; live Pages and run artifacts are the current generated editions. A failed build leaves the previous successful publication available, so check Actions and the site's build record when verifying an update.

For a local website preview, Python 3 alone is sufficient:

```sh
python scripts/preview.py
```

Open `http://127.0.0.1:8766/`. This generates fresh static pages under the ignored `build/preview/` directory and serves them locally without changing the checked-in starter snapshots. After editing source files, run `python scripts/preview.py --build-only` and refresh the browser. Stop the server with Ctrl+C. The PDF link identifies and opens the locally preserved snapshot by its actual version. The v0.6 HTML/TeX and historical v0.2 PDF remain different editions until a matching fresh PDF snapshot is generated. Use `--port 8767` to choose another port or `--build-only` to generate without starting a server.

The website uses a persistent searchable index and a spacious reading column. On mobile, the index folds into a native expandable catalog. Queries and appearance choices persist only in the current browser tab. Fonts are served locally; their licenses are included under `docs/assets/fonts/`.

Run the website content and navigation regression checks with `python -m unittest discover -s tests -v`; Actions runs the same checks before generating the handbook.

To preview a newly compiled PDF as well, install Python 3, TeX Live, BibTeX, and latexmk:

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

Submit public sources and synthetic examples. Do not include private chats, unpublished results, datasets, credentials, internal notes, or personal paths. New entries are proposed; adopted status requires explicit unanimous consensus evidence, a decision date and an accessible public link.

Original handbook prose uses **CC BY 4.0**; build scripts and site code use **MIT**. Third-party sources retain their own rights. See [license scope](LICENSE.md).

[GitHub PDF rendering documentation](https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files#rendering-pdf-documents) · [Artifact downloads](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts)

## Editorial skill and validation

Use [.agents/skills/plalelab-glossry-edit/SKILL.md](.agents/skills/plalelab-glossry-edit/SKILL.md). Its template, structural JSON schema and content/page contracts define cited statements, source tiers, semantic kinds and relationship conditions. The semantic validator also rejects missing citation IDs, dangling links, incompatible or cyclic is-a relations and false adoption records. Yellow/green tags describe Lab adoption only; all six current working definitions are yellow.

The internal proposal is stored in JSON and generated as `lab-guide.html`; it contains no chat transcript. Strict is-a nesting currently connects LLM to Model. Agent uses LLM in the LLM-based scope; Harness supports/orchestrates Workflow and Agent. Old terms have left the active source and generated routes; their earlier editions remain in Git history and historical PDF provenance.

Publishing to `main` runs the validation, fresh PDF compilation and Pages deployment together. Verify the deployed edition and source commit in the live build record; a failed run leaves the previous successful edition available.

Harness contains the canonical [Harness vs Workflow comparison](https://williamq96.github.io/plale-lab-glossary/terms/harness.html#harness-vs-workflow), including an illustrative schema-extraction experiment and limits of reproducibility. Workflow links to that section; no duplicate comparison entry is maintained.
