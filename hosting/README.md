# Open AI Glossary live mirror

`https://glossary.williamq.dev/` reads `https://williamq96.github.io/plale-lab-glossary/` through a fixed-origin reverse proxy. Paths such as `/terms/harness.html`, `/assets/style.css`, `/glossary.pdf` and `/BUILD-INFO.json` map to the same published paths beneath the GitHub project prefix. Relative links keep the mirror hostname; external citations retain their original destinations.

GitHub Pages is the single publishing source. No second content repository, scheduled copy or deployment webhook is necessary. After a successful Pages build, mirror requests read the published source. Responses are `Cache-Control: no-store`, upstream requests ask for revalidation, and neither the app nor its Cloudflare edge adds a stored content copy. GitHub's upstream cache behavior and availability remain relevant; this does not publish uncommitted edits or make a failed Pages build live.

The mirror is deliberately public. It forwards no cookies, Authorization headers or user identity to GitHub. Only GET/HEAD read the fixed origin; arbitrary targets, traversal and redirects outside this glossary are rejected. A temporary upstream failure produces an error rather than silently serving an obsolete local copy. The existing Cloudflare zone adds its analytics beacon to HTML; verification excludes only that observed edge addition when comparing glossary bytes. Assets, PDF and metadata are compared without normalization.

## Deployment

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
