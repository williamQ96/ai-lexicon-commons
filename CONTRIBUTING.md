# Contributing to the living glossary

Edit `data/handbook.json`, the shared source for the website and PDF. Readers are assumed to have academic and engineering experience; prioritize a useful boundary or ambiguity over introductory instruction.

1. Copy [the definition-entry template](templates/definition-entry.json) into the terms array. Use one core term per entry and a unique stable slug.
2. State the chosen working definition and scope, inclusions/exclusions, ambiguities, and operational criteria where applicable. Explain not applicable, or mark unresolved criteria pending.
3. Add public sources to the sources object and reference their IDs from the term. Prefer applicable standards, disciplinary consensus, and authoritative definitions; then peer-reviewed literature. Peer review alone does not establish consensus. Attribute preprints, first-party documentation, and engineering practices when used for newer terms.
4. Preserve differing meanings and source attribution. Explain this project's chosen interpretation instead of presenting an adaptation as the source's exact definition.
5. Set entry version and revision date, add valid related-term slugs, and keep new entries proposed. Adopted status requires an explicit team decision date and public link.
6. Commit the JSON change and open a pull request; generated files need not be committed. Actions builds fresh pages, TeX, and PDF from the shared source and uploads a review artifact. Review the website and PDF in that artifact. After merge to `main`, a successful build publishes both together. Pull requests do not publish. See the [editing workflow](README.md) for local preview commands and build provenance.

Use public material and synthetic examples. Keep private chats, unpublished results, datasets, credentials, internal notes, and personal paths out of this public project.

Original prose is CC BY 4.0 and code is MIT, as described in [license scope](LICENSE.md). Preserve third-party rights and attribution. Do not add another person's material unless it may be shared under the relevant terms.
