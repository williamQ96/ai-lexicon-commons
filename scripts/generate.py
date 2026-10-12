#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 William Qiu
"""Generate the website, TeX, bibliography, and snapshot record from public JSON."""
import argparse
import base64
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import textwrap

from web_layout import navigation, search_text

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/handbook.json"
REPO = "https://github.com/williamQ96/plale-lab-glossary"

def esc(value):
    return html.escape(str(value), quote=True)

def tex(value):
    replacements = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}",
                    "$": r"\$", "&": r"\&", "#": r"\#", "_": r"\_",
                    "%": r"\%", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(replacements.get(c, c) for c in str(value))

from content import validate

def status_text(term):
    return "Proposed; pending team confirmation." if term["status"] == "proposed" else "Adopted within the stated scope; see the recorded team decision."

def adoption_record(term):
    return "none recorded." if term["status"] == "proposed" else term["adoption"]["date"] + "; " + term["adoption"]["url"]

def adoption_html(term):
    if term["status"] == "proposed":
        return "none recorded."
    return '<a href="' + esc(term["adoption"]["url"]) + '">' + esc(term["adoption"]["date"]) + '</a>'

def paragraph_list(items):
    return "".join("<p>" + esc(item) + "</p>" for item in items)

def bullet_list(items):
    return "<ul>" + "".join("<li>" + esc(item) + "</li>" for item in items) + "</ul>"

def page(book, title, content, digest, prefix="", source_commit="", run_url="", sidebar=""):
    proposed = sum(t['status'] == 'proposed' for t in book['terms'])
    certification_status = f"Repository definitions: {proposed} proposed / {len(book['terms']) - proposed} certified by consensus"
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="description" content="A living glossary for clear research and engineering communication.">'
            '<title>' + esc(title) + ' | ' + esc(book['short_title']) + '</title>'
            '<link rel="stylesheet" href="' + prefix + 'assets/style.css">'
            '<script src="' + prefix + 'assets/search.js" defer></script></head><body data-index-url="' + prefix + 'index.html">'
            '<a class="skip" href="#main">Skip to content</a>'
            '<header class="site-header"><a class="brand" href="' + prefix + 'index.html">OPEN AI <span>GLOSSARY</span></a>'
            '<nav aria-label="Main navigation"><a href="' + prefix + 'index.html">Index &amp; search</a>'
            '<a href="' + prefix + 'lab-guide.html">Repository guide</a><a href="' + prefix + 'glossary.pdf">PDF</a><a href="' + REPO + '">Contribute on GitHub</a>'
            '<button id="theme-toggle" type="button" hidden>Dark</button></nav></header>'
            '<div class="workspace' + ('' if sidebar else ' standalone') + '">' + sidebar +
            '<div class="reading-panel"><main id="main" tabindex="-1">' + content + '</main>'
            '<footer><p>Living glossary / Version ' + esc(book["version"]) + ' / Updated ' + esc(book["updated"]) +
            ' / Content ' + digest[:12] + '</p><p>' + esc(certification_status) + '.</p>'
            '<p>Copyright 2026 William Qiu. Original prose <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>; '
            'site code <a href="' + REPO + '/blob/main/LICENSES/MIT.txt">MIT</a>. Third-party sources retain their own rights. '
            '<a href="' + REPO + '/blob/main/LICENSE.md">License scope</a></p>' +
            ('<p>Build <a href="' + REPO + '/commit/' + esc(source_commit) + '">' + esc(source_commit[:12]) + '</a> / '
             '<a href="' + prefix + 'build-record.html">PDF build record</a></p>' if source_commit else '') +
            '</footer></div></div></body></html>\n')

def generate(book, digest, source_commit="", run_url=""):
    from render import render_book
    return render_book(book, digest, page, source_commit, run_url)

def snapshot(book, digest, source_commit, run_url):
    pdf = ROOT / "build/main.pdf"
    assert pdf.read_bytes().startswith(b"%PDF-"), "Compiled PDF missing or invalid"
    shutil.copyfile(pdf, ROOT / "docs/glossary.pdf")
    record = {"source_sha256":digest, "content_version":book["version"],
              "pdf_sha256":hashlib.sha256(pdf.read_bytes()).hexdigest(),
              "source_commit":source_commit or None, "build_run":run_url or None}
    (ROOT / "docs/PDF-SNAPSHOT.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    prose = ("# Compiled handbook snapshot\n\nThis PDF is generated from data/handbook.json, the same source as the searchable website. "
             "Repository adoption is recorded separately for each definition.\n\n"
             "- Content version: " + book["version"] + "\n- Source content SHA-256: " + digest +
             "\n- PDF SHA-256: " + record["pdf_sha256"] + "\n")
    if source_commit:
        prose += "- Source commit: [" + source_commit + "](" + REPO + "/commit/" + source_commit + ")\n"
    if run_url:
        prose += "- Successful build: [GitHub Actions](" + run_url + ")\n"
    prose += ("\nThe main-branch Actions workflow generates the website and this PDF from the same source, "
              "checks their content hash and PDF checksum, and publishes the fresh site artifact after a successful build. "
              "Pull-request builds provide review artifacts and do not publish. Checked-in starter previews are historical snapshots.\n")
    (ROOT / "docs/PDF-SNAPSHOT.md").write_text(prose, encoding="utf-8")
    commit_link = ('<a href="' + REPO + '/commit/' + esc(source_commit) + '">' + esc(source_commit) + '</a>') if source_commit else 'Local preview; no commit recorded.'
    run_link = ('<a href="' + esc(run_url) + '">Successful build run</a>') if run_url else 'Local preview; no run recorded.'
    body = ('<section class="intro"><h1>PDF build record.</h1>'
            '<p class="lead">The website and PDF are generated together from the same content source.</p></section>'
            '<section class="policy"><h2>Published edition</h2><dl>'
            '<dt>Content version</dt><dd>' + esc(book["version"]) + '</dd>'
            '<dt>Source commit</dt><dd>' + commit_link + '</dd>'
            '<dt>Build run</dt><dd>' + run_link + '</dd>'
            '<dt>Shared-source SHA-256</dt><dd><code>' + digest + '</code></dd>'
            '<dt>PDF SHA-256</dt><dd><code>' + record["pdf_sha256"] + '</code></dd></dl>'
            '<p><a href="glossary.pdf">Read the compiled PDF</a> / <a href="index.html">Return to the index</a></p>'
            '<p>The PDF also prints its source commit and build run. Publication follows successful main-branch builds; '
            'pull-request builds provide review artifacts.</p>'
            '<p><a href="PDF-SNAPSHOT.json">Machine-readable JSON record</a></p></section>')
    (ROOT / "docs/build-record.html").write_text(page(book, "Build record", body, digest,
        source_commit=source_commit, run_url=run_url), encoding="utf-8")


def emit_export(outputs):
    export = dict(outputs)
    for relative in ("docs/PDF-SNAPSHOT.md","docs/PDF-SNAPSHOT.json","LICENSES/CC-BY-4.0.txt"):
        path = ROOT / relative
        if path.exists():
            export[relative] = path.read_text(encoding="utf-8")
    encoded = base64.b64encode(json.dumps(export, ensure_ascii=True).encode()).decode()
    print("HANDBOOK_TEXT_BASE64_BEGIN")
    print("\n".join(textwrap.wrap(encoded, 76)))
    print("HANDBOOK_TEXT_BASE64_END")
    print("HANDBOOK_PDF_BASE64_BEGIN")
    print("\n".join(textwrap.wrap(base64.b64encode((ROOT / "docs/glossary.pdf").read_bytes()).decode(), 76)))
    print("HANDBOOK_PDF_BASE64_END")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--snapshot", action="store_true")
    parser.add_argument("--export", action="store_true")
    parser.add_argument("--source-commit", default="")
    parser.add_argument("--run-url", default="")
    args = parser.parse_args()
    raw = DATA_PATH.read_bytes()
    book = json.loads(raw)
    validate(book)
    digest = hashlib.sha256(raw).hexdigest()
    outputs = generate(book, digest, args.source_commit, args.run_url)
    if args.check:
        stale = [p for p, content in outputs.items()
                 if not (ROOT / p).exists() or (ROOT / p).read_text(encoding="utf-8") != content]
        record_path = ROOT / "docs/PDF-SNAPSHOT.json"
        record = json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else {}
        pdf_path = ROOT / "docs/glossary.pdf"
        if record.get("source_sha256") != digest:
            stale.append("docs/glossary.pdf snapshot content")
        elif not pdf_path.exists() or hashlib.sha256(pdf_path.read_bytes()).hexdigest() != record.get("pdf_sha256"):
            stale.append("docs/glossary.pdf snapshot checksum")
        if args.source_commit and record.get("source_commit") != args.source_commit:
            stale.append("PDF snapshot source commit")
        if args.run_url and record.get("build_run") != args.run_url:
            stale.append("PDF snapshot build run")
        if stale:
            raise SystemExit("Generated content is stale: " + ", ".join(stale))
        print("Generated pages, TeX, bibliography, and snapshot content hash match the shared source.")
    else:
        terms_dir = ROOT / "docs/terms"
        if terms_dir.exists():
            for previous in terms_dir.glob("*.html"):
                if previous.relative_to(ROOT).as_posix() not in outputs:
                    previous.unlink()
        for relative, content in outputs.items():
            target = ROOT / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")
        print("Generated", len(outputs), "text files for", len(book["terms"]), "terms; source", digest)
    if args.snapshot:
        snapshot(book, digest, args.source_commit, args.run_url)
    if args.export:
        emit_export(outputs)

if __name__ == "__main__":
    main()
