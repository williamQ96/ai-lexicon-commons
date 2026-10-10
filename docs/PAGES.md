# Public handbook hosting

The public reading interface is served from the repository's `main` branch, `docs/` folder, using GitHub Pages. The index, linked term pages, and PDF are generated from `data/handbook.json`.

[Read the handbook](https://williamq96.github.io/plale-lab-glossary/)

GitHub's branch publishing serves the committed static files; `docs/.nojekyll` disables Jekyll processing. The compilation workflow retains only `contents: read`, does not push files, and uses no new credentials. GitHub handles its branch publishing workflow separately.

Update the shared content, regenerate the pages and TeX, compile and record the PDF snapshot, and review the outputs before committing. CI checks text generation and snapshot hashes to detect drift. The public website updates from the committed `docs/` folder.

No custom domain or additional account integration is configured.
