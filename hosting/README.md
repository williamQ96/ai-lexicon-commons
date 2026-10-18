# AI Lexicon Commons live mirror

**AI Lexicon Commons — An open, community-maintained reference for AI terminology and concepts.**

`https://glossary.williamq.dev/` reads `https://williamq96.github.io/ai-lexicon-commons/` through a fixed-origin reverse proxy. Paths such as `/terms/harness.html`, `/assets/style.css`, `/glossary.pdf` and `/BUILD-INFO.json` map to the same published paths beneath the GitHub project prefix. Relative links keep the mirror hostname; external citations retain their original destinations.

GitHub Pages is the single publishing source. No second content repository, scheduled copy or deployment webhook is necessary. After a successful Pages build, mirror requests read the published source. Responses are `Cache-Control: no-store`, upstream requests ask for revalidation, and neither the app nor its Cloudflare edge adds a stored content copy. GitHub's upstream cache behavior and availability remain relevant; this does not publish uncommitted edits or make a failed Pages build live.

The mirror is deliberately public. It forwards no cookies, Authorization headers or user identity to GitHub. Only GET/HEAD read the fixed origin; arbitrary targets, traversal and redirects outside this glossary are rejected. A temporary upstream failure produces an error rather than silently serving an obsolete local copy. The existing Cloudflare zone adds its analytics beacon to HTML; verification excludes only that observed edge addition when comparing glossary bytes. Assets, PDF and metadata are compared without normalization.

## Deployment history

- Service path `/volume2/docker/williamq-glossary`, release `20261012-r1`.
- Container `williamq-glossary-mirror`, image `williamq/glossary-mirror:2026-10-12-r1`.
- NAS loopback `127.0.0.1:18195` to container `8000`; read-only container, user 1026:100, no credentials or persistent content mounted.
- DSM owns HTTPS proxy and certificate assignments. HTTP redirects to HTTPS except the narrow public ACME challenge path. The read-only challenge mount permits DSM-managed certificate renewal.
- Cloudflare owns active DNS and HTTPS edge; Full (strict) TLS remains enabled. Only the glossary record is added.

Use the `williamq-hosting` skill for credentials, DNS, DSM administration and preflight. `deploy.py stage` creates an allowlisted first release and refuses an existing service directory; inspect the receipt before any subsequent upgrade. `deploy.py http` creates only this host's HTTP proxy. HTTPS/certificate provisioning uses the skill's managed DSM helper. Credentials remain in the user-designated protected file, outside Git and release bundles.

Run `python -m unittest discover -s hosting -v` locally; the same checks run in the Pages workflow. `/_mirror-health` is a liveness probe; verify published `BUILD-INFO.json`, HTML, assets and PDF as well to establish upstream health.

## Evidence and rollback

`deployment.json` records release/image hashes and the service port. `https.json` records public proxy/certificate metadata. `validation.json` records the deployed source and byte comparisons. Pre-change DNS/proxy snapshots and release archives are kept in ignored `build/hosting-backup/` and `build/`; no application data needs backup.

To remove the alias, use the skill's supported DNS/DSM APIs to remove only its recorded DNS record and two glossary proxy UUIDs, then stop only `williamq-glossary-mirror`. Preserve its release directory and certificate for recovery; do not delete volumes or modify other hosts, certificates, account stores or router forwarding. GitHub Pages continues to publish independently. For future code upgrades, retain the prior image/compose and switch only this service, retaining the ACME mount and loopback binding.

## Repository rename and release history (2026-10-18, v0.8)

The GitHub repository is now `williamQ96/open-AI-glossary`; its Pages path is `https://williamq96.github.io/open-AI-glossary/`. The old project Pages path returned 404. Both the main-branch publication guard and the mirror's fixed origin now use the current identity. The existing Git remote alias and local project directory are retained.

NAS release at that verification: `20261018-r2`, image `williamq/glossary-mirror:2026-10-18-r2`, at the same service path and loopback port. See [the immutable deployment receipt](deployment-20261018-r2.json). It retains the prior image and `/volume2/docker/williamq-glossary/compose.pre-20261018-r2.yaml` for rollback. Read-only operation, the ACME mount and user 1026:100 are preserved. No glossary content or account state is stored on the mirror.

For a subsequent scoped upgrade, run `python hosting/upgrade.py --release YYYYMMDD-rN` with a fresh release ID. It verifies the previous healthy container, captures compose rollback, packages only server code and its Dockerfile, verifies runtime hashes and checks health before accepting the release. The first 20261018-r1 attempt rolled back because its 30-second acceptance window ended before the first scheduled health check completed; r2 uses a 180-second window and passed. Retain both attempts' NAS releases and compose backups.

Content v0.8 adds Bias, Reasoning, Human in the loop and Model in the loop. Pages run [39164173590](https://github.com/williamQ96/open-AI-glossary/actions/runs/39164173590) published commit `4961ee28a29bc2b55b8d86c4dd8756b687e9989f` after 22 content/publication tests, four mirror tests and fresh PDF compilation. Twenty public resources, including all ten term pages and the PDF, match the Pages source; HTML comparisons exclude only the existing Cloudflare analytics addition.

## AI Lexicon Commons v0.9 (verified 2026-10-18)

The owner requested the project name **AI Lexicon Commons**, with the tagline **An open, community-maintained reference for AI terminology and concepts.** The same GitHub repository is now `williamQ96/ai-lexicon-commons`; its previous repository URLs redirect to that identity. Origin now uses its canonical Git URL. The local checkout and `glossary.williamq.dev` hostname remain stable.

Current mirror release is `20261018-r3`, image `williamq/glossary-mirror:2026-10-18-r3`; see [deployment receipt](deployment-20261018-r3.json). It preserves the service path, loopback port, read-only operation, UID/GID and ACME mount. `compose.pre-20261018-r3.yaml` and the previous image remain as code rollback artifacts; the former Pages project origin itself no longer serves the renamed site, so do not mistake a code rollback for restoring that obsolete URL.

Pages run [39165174303](https://github.com/williamQ96/ai-lexicon-commons/actions/runs/39165174303) published `e3127b4181cadc0ddb1865e05e717478c2e14490` after 22 glossary/publication checks, four mirror checks and fresh PDF compilation. Twenty resources match the new Pages origin. The website title, metadata, navigation, contribution links and PDF title/tagline use the new identity. All ten term definitions, slugs and adoption states are preserved. Historical snapshots and receipts remain unchanged.

The canonical editor is `ai-lexicon-commons-edit`; `open-ai-glossary-edit` forwards to it. Both the installed skill and repository copy are updated. The WilliamQ Research entry uses the new title, exact tagline and GitHub destination while preserving its historical catalog ID/deep link.
