#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 William Qiu
"""Generate an isolated HTML preview without TeX or tracked build output."""
import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
from generate import DATA_PATH, ROOT, generate, validate


def prepare():
    raw = DATA_PATH.read_bytes()
    book = json.loads(raw)
    validate(book)
    digest = hashlib.sha256(raw).hexdigest()
    record = json.loads((ROOT / 'docs/PDF-SNAPSHOT.json').read_text(encoding='utf-8'))
    pdf = ROOT / 'docs/glossary.pdf'
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != record['pdf_sha256']:
        raise ValueError('PDF checksum does not match its edition record')
    current_pdf = record['source_sha256'] == digest
    edition = record['content_version']
    target = ROOT / "build/preview"
    target.mkdir(parents=True, exist_ok=True)
    outputs = generate(book, digest)
    terms = target / "terms"
    if terms.exists():
        expected = {Path(path).name for path in outputs if path.startswith("docs/terms/")}
        for path in terms.glob("*.html"):
            if path.name not in expected:
                path.unlink()
    for relative, content in outputs.items():
        if not relative.startswith("docs/"):
            continue
        path = target / Path(relative).relative_to("docs")
        path.parent.mkdir(parents=True, exist_ok=True)
        # Keep the checked-in PDF's honest edition; never relabel it with fresh JSON.
        if path.suffix == ".html":
            for prefix in ("", "../"):
                content = content.replace('href="' + prefix + 'glossary.pdf"',
                    'href="' + prefix + 'previous-glossary.pdf"')
            content = content.replace('>PDF</a>', '>' + ('PDF' if current_pdf else 'Previous PDF') + ' · v' + edition + '</a>')
            if not current_pdf:
                content = content.replace('</main>', '<p class="pdf-edition-note">This preview is content v' + book['version'] + '. The linked PDF is the historical v' + edition + ' snapshot; it does not match this glossary edition.</p></main>')
        path.write_text(content, encoding="utf-8", newline="\n")
    shutil.copytree(ROOT / "docs/assets", target / "assets", dirs_exist_ok=True)
    shutil.copyfile(pdf, target / 'previous-glossary.pdf')
    (target / 'PREVIOUS-PDF.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--build-only", action="store_true")
    args = parser.parse_args()
    target = prepare()
    print("Generated HTML preview: " + str(target), flush=True)
    if args.build_only:
        return
    handler = partial(SimpleHTTPRequestHandler, directory=str(target))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"Preview: http://127.0.0.1:{args.port}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
