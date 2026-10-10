# Public handbook hosting

[Read the handbook](https://williamq96.github.io/plale-lab-glossary/) · [Current PDF](https://williamq96.github.io/plale-lab-glossary/glossary.pdf) · [Build record](https://williamq96.github.io/plale-lab-glossary/PDF-SNAPSHOT.json)

GitHub Pages uses **GitHub Actions** as its publishing source. The workflow generates the index, linked term pages, TeX, bibliography, and compiled PDF from `data/handbook.json`, then publishes one fresh site artifact after a successful `main` build. It never publishes the committed starter `docs/` tree directly.

Content-only edits work: commit the JSON, review the pull-request build artifact, and merge. No generated file commit is needed. The current site/PDF share a content hash, source commit, and build run. Check the site footer or JSON build record to identify the published edition; failed builds keep the preceding successful edition.

The build job has only `contents: read`. Pull requests build review artifacts and cannot deploy. The separate deployment job is restricted to this repository's `main` branch, needs a successful build, checks out no source, and has only `pages: write` and `id-token: write`. All direct actions are pinned official GitHub actions. There is no repository-write permission or stored credential.

Workflow concurrency serializes runs per branch so older main builds finish before newer builds publish. No custom domain or additional account integration is configured.

[Workflow](../.github/workflows/build-pdf.yml) · [GitHub custom Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
