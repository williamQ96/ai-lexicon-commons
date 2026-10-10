# Optional GitHub Pages reading page

**Proposal only. Pages has not been enabled or deployed.**

The current build publishes a downloadable PDF artifact. A committed PDF can also be previewed directly in GitHub.

For a stable public reading page, a later change could add a small `docs/index.html` linking to the existing compiled snapshot at `docs/glossary.pdf`. After owner approval, GitHub Pages could serve the `main` branch's `docs/` folder. A `.nojekyll` file would make this a plain static site. This uses GitHub's Pages hosting and requires no new credentials, but snapshot updates remain manual.

A second option is a separately reviewed Actions deployment that builds the PDF and publishes a static index through official Pages actions. It would require Pages setup and explicit `pages: write` and `id-token: write` permissions for the deployment job. Keep those permissions out of the current compilation workflow.

Before enabling either option, agree on public content, deployment method, version labeling, and approval process. The expected project URL would be `https://williamq96.github.io/plale-lab-glossary/` if standard project Pages hosting is enabled; it is not a live site now.

[GitHub Pages documentation](https://docs.github.com/en/pages)
