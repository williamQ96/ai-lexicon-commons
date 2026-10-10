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

def validate(book):
    terms = book["terms"]
    slugs = {t["slug"] for t in terms}
    assert len(slugs) == len(terms), "Duplicate term slug"
    for t in terms:
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", t["slug"]), "Invalid slug"
        for key in ("title", "definition", "scope", "operational", "adaptation",
                    "entry_version", "updated"):
            assert isinstance(t[key], str) and t[key].strip(), "Missing " + key
        assert t["status"] in ("proposed", "adopted"), "Invalid status"
        assert set(t["related"]) <= slugs, "Unknown related term"
        assert set(t["sources"]) <= set(book["sources"]), "Unknown source"
        if t["status"] == "adopted":
            assert t["adoption"]["date"] and t["adoption"]["url"], "Adoption needs decision"
            assert t["adoption"]["url"].startswith("https://"), "Decision link must be public HTTPS"
    for source in book["sources"].values():
        assert source["url"].startswith("https://"), "Public sources must use HTTPS"

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

def page(book, title, content, digest, prefix="", source_commit="", run_url=""):
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="description" content="A living glossary for clear research and engineering communication.">'
            '<title>' + esc(title) + ' | Plale Lab Glossary</title>'
            '<link rel="stylesheet" href="' + prefix + 'assets/style.css"></head><body>'
            '<a class="skip" href="#main">Skip to content</a>'
            '<header class="site-header"><a class="brand" href="' + prefix + 'index.html">PLALE LAB <span>GLOSSARY</span></a>'
            '<nav aria-label="Main navigation"><a href="' + prefix + 'index.html">Index &amp; search</a>'
            '<a href="' + prefix + 'glossary.pdf">PDF</a><a href="' + REPO + '">Contribute on GitHub</a></nav></header>'
            '<main id="main">' + content + '</main>'
            '<footer><p>Living glossary / Version ' + esc(book["version"]) + ' / Updated ' + esc(book["updated"]) +
            ' / Content ' + digest[:12] + '</p><p>Working proposal; pending team confirmation.</p>'
            '<p>Copyright 2026 William Qiu. Original prose <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>; '
            'site code <a href="' + REPO + '/blob/main/LICENSES/MIT.txt">MIT</a>. Third-party sources retain their own rights. '
            '<a href="' + REPO + '/blob/main/LICENSE.md">License scope</a></p>' +
            ('<p>Build <a href="' + REPO + '/commit/' + esc(source_commit) + '">' + esc(source_commit[:12]) + '</a> / '
             '<a href="' + prefix + 'PDF-SNAPSHOT.json">PDF build record</a></p>' if source_commit else '') +
            '</footer></body></html>\n')

def generate(book, digest, source_commit="", run_url=""):
    outputs = {}
    terms = sorted(book["terms"], key=lambda t: t["title"].casefold())
    by_slug = {t["slug"]: t for t in terms}
    groups = {}
    for t in terms:
        groups.setdefault(t["title"][0].upper(), []).append(t)
    letters = "".join('<a href="#letter-' + letter + '">' + letter + '</a>' for letter in groups)
    rows = []
    for letter, members in groups.items():
        section = '<section class="letter-group" id="letter-' + letter + '"><h2>' + letter + '</h2><div>'
        for t in members:
            search = " ".join([t["title"], t["full_name"], *t["aliases"], t["definition"],
                               t["scope"], *t["includes"], *t["excludes"], *t["ambiguities"],
                               t["operational"], t["adaptation"],
                               *[book["sources"][s]["title"] for s in t["sources"]]])
            section += ('<article class="term-row" data-search="' + esc(search.casefold()) + '">'
                        '<div><a class="term-name" href="terms/' + t["slug"] + '.html">' + esc(t["title"]) +
                        '</a><p class="full-name">' + esc(t["full_name"]) + '</p></div><p>' + esc(t["definition"]) +
                        '</p><span class="status">' + esc(t["status"].capitalize()) + '</span></article>')
        rows.append(section + '</div></section>')
    index = ('<section class="intro"><p class="eyebrow">A SHARED LANGUAGE FOR RESEARCH &amp; ENGINEERING</p>'
             '<h1>A living glossary.</h1><p class="lead">' + esc(book["introduction"][0]) + '</p>'
             + paragraph_list(book["introduction"][1:]) + '<p class="notice">' + esc(book["status"]) +
             '. The definitions below are chosen for this draft; they have not been ratified by the lab.</p></section>'
             '<section class="index-controls" aria-label="Find a term"><label for="search">Search the glossary</label>'
             '<div class="search-line"><input id="search" type="search" placeholder="Try AI, model, provenance..." autocomplete="off">'
             '<button id="clear-search" type="button">Clear</button></div>'
             '<p id="result-count" aria-live="polite">' + str(len(terms)) + ' terms</p>'
             '<nav class="alphabet" aria-label="Alphabetical index">' + letters + '</nav></section>'
             '<div id="term-index">' + "".join(rows) + '</div><p id="no-results" hidden>No terms match. Try another word or clear the search.</p>'
             '<section class="policy"><h2>How this glossary chooses its meanings</h2>' + paragraph_list(book["source_policy"]) +
             '<h3>Team review and revision</h3><p>' + esc(book["adoption_policy"]) +
             '</p><p><a href="' + REPO + '/blob/main/CONTRIBUTING.md">Propose a definition or revision</a></p></section>'
             '<noscript><p>Search requires JavaScript. All terms and alphabetical links remain available above.</p></noscript>'
             '<script src="assets/search.js" defer></script>')
    outputs["docs/index.html"] = page(book, "Index", index, digest, source_commit=source_commit, run_url=run_url)
    for t in terms:
        related = "".join('<a href="' + s + '.html">' + esc(by_slug[s]["title"]) + '</a>' for s in t["related"])
        sources = ""
        for sid in t["sources"]:
            s = book["sources"][sid]
            sources += ('<li><a href="' + esc(s["url"]) + '">' + esc(s["title"]) + '</a><p>' + esc(s["author"]) +
                        ' / ' + esc(s["kind"]) + '</p><p>' + esc(s["version"]) + '. ' + esc(s["locator"]) +
                        '. Accessed ' + esc(s["accessed"]) + '.</p></li>')
        if not sources:
            sources = '<li>Original project proposal. No external authoritative or consensus definition is claimed.</li>'
        body = ('<a class="back" href="../index.html">Back to alphabetical index</a>'
                '<div class="term-layout"><article><p class="eyebrow">WORKING DEFINITION</p><h1 class="term-title">' +
                esc(t["title"]) + '</h1><p class="subtitle">' + esc(t["full_name"]) + '</p><p class="lead">' +
                esc(t["definition"]) + '</p><p class="notice">' + esc(status_text(t)) + '</p>'
                '<section><h2>Scope</h2><p>' + esc(t["scope"]) + '</p></section>'
                '<div class="boundaries"><section><h2>Includes</h2>' + bullet_list(t["includes"]) +
                '</section><section><h2>Excludes</h2>' + bullet_list(t["excludes"]) + '</section></div>'
                '<section><h2>Ambiguities and boundaries</h2>' + bullet_list(t["ambiguities"]) + '</section>'
                '<section><h2>Operational criteria</h2><p>' + esc(t["operational"]) + '</p></section>'
                '<section><h2>This project\'s chosen working meaning</h2><p>' + esc(t["adaptation"]) + '</p></section>'
                '<section class="sources"><h2>Versioned sources</h2><ol>' + sources + '</ol></section></article>'
                '<aside><h2>Related terms</h2><nav aria-label="Related terms">' + related + '</nav><h2>Entry record</h2>'
                '<p>Version ' + esc(t["entry_version"]) + '<br>Updated ' + esc(t["updated"]) +
                '<br>Status: ' + esc(t["status"]) + '<br>Adoption decision: ' + adoption_html(t) + '</p>'
                '<a href="' + REPO + '/blob/main/data/handbook.json">View source content</a></aside></div>')
        outputs["docs/terms/" + t["slug"] + ".html"] = page(book, t["title"], body, digest, "../", source_commit, run_url)
    outputs["docs/.nojekyll"] = ""
    outputs["docs/BUILD-INFO.json"] = json.dumps({"content_version":book["version"], "updated":book["updated"],
        "source":"data/handbook.json", "source_sha256":digest, "terms":len(terms),
        "source_commit":source_commit or None, "build_run":run_url or None}, indent=2) + "\n"
    latex = [r"\documentclass[11pt,letterpaper]{article}", r"\usepackage[T1]{fontenc}",
             r"\usepackage[utf8]{inputenc}", r"\usepackage{lmodern}", r"\usepackage[margin=1in]{geometry}",
             r"\usepackage{microtype}", r"\usepackage{xcolor}", r"\usepackage{hyperref}",
             r"\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue,citecolor=blue}",
             r"\pdfinfoomitdate=1", r"\pdftrailerid{}", r"\Urlmuskip=0mu plus 1mu",
             r"\setlength{\parindent}{0pt}", r"\setlength{\parskip}{0.45em}",
             r"\newcommand{\field}[2]{\par\textbf{#1.} #2\par}",
             "% Generated from data/handbook.json. Edit the JSON, not this file.",
             r"\begin{document}", r"\section*{" + tex(book["title"]) + "}",
             r"\textbf{Living glossary --- Version " + tex(book["version"]) + " --- " + tex(book["updated"]) + "}",
             r"\par\textbf{" + tex(book["status"]) + ".}",
             *[tex(p) + "\n" for p in book["introduction"]],
             r"\subsection*{Source policy}", *[tex(p) + "\n" for p in book["source_policy"]],
             r"\subsection*{Team review}", tex(book["adoption_policy"]),
             r"\subsection*{Licensing}", r"Copyright 2026 William Qiu. Original prose: \href{https://creativecommons.org/licenses/by/4.0/}{CC BY 4.0}. Build scripts and site code: MIT. Third-party sources retain their own rights.",
             r"\newpage\section*{Alphabetical index}",
             r"Select a term to navigate within this PDF. The website also offers search.",
             r"\begin{itemize}"]
    for t in terms:
        latex.append(r"\item \hyperlink{term-" + t["slug"] + "}{" + tex(t["title"]) + "}" +
                     (" --- " + tex(t["full_name"]) if t["full_name"] else ""))
    latex.append(r"\end{itemize}")
    for t in terms:
        latex.extend([r"\newpage\hypertarget{term-" + t["slug"] + "}{}",
                      r"{\small PLALE LAB LIVING GLOSSARY}\par",
                      r"\section*{\Huge " + tex(t["title"]) + "}",
                      tex(t["full_name"]) + r"\par" if t["full_name"] else "",
                      r"\textbf{" + tex(t["definition"]) + "}",
                      r"\par\textit{" + tex(status_text(t)) + "}",
                      r"\field{Scope}{" + tex(t["scope"]) + "}"])
        for key, heading in [("includes","Includes"),("excludes","Excludes"),("ambiguities","Ambiguities and boundaries")]:
            latex.extend([r"\textbf{" + heading + "}", r"\begin{itemize}",
                          *[r"\item " + tex(p) for p in t[key]], r"\end{itemize}"])
        latex.extend([r"\field{Operational criteria}{" + tex(t["operational"]) + "}",
                      r"\field{Chosen working meaning}{" + tex(t["adaptation"]) + "}"])
        if t["sources"]:
            latex.append(r"\field{Sources}{\cite{" + ",".join(t["sources"]) + r"}. See versioned reference records below.}")
        else:
            latex.append(r"\field{Sources}{Original project proposal; no external authority claimed.}")
        latex.append(r"\field{Entry record}{Version " + tex(t["entry_version"]) + "; updated " +
                     tex(t["updated"]) + "; status: " + tex(t["status"]) + "; adoption decision: " + tex(adoption_record(t)) + "}")
        latex.append(r"\field{Related terms}{" + "; ".join(
            r"\hyperlink{term-" + s + "}{" + tex(by_slug[s]["title"]) + "}" for s in t["related"]) + "}")
    latex.extend([r"\newpage\section*{Build provenance}",
                  r"Source content SHA-256: \nolinkurl{" + digest + "}."])
    if source_commit:
        latex.append(r"\par Source commit: \href{" + REPO + "/commit/" + source_commit + r"}{\nolinkurl{" + source_commit + "}}.")
    if run_url:
        latex.append(r"\par Build run: \url{" + run_url + "}.")
    latex.extend([r"\bibliographystyle{plain}", r"\bibliography{references}", r"\end{document}"])
    outputs["main.tex"] = "\n".join(latex) + "\n"
    bib = []
    for sid, s in book["sources"].items():
        bib.append("@misc{" + sid + ",\n  author = {{" + tex(s["author"]) +
                   "}},\n  title = {{" + tex(s["title"]) + "}},\n  year = {" + s["year"] +
                   "},\n  howpublished = {" + tex(s["kind"]) + "},\n  note = {" +
                   tex(s["version"] + ". " + s["locator"] + ". Accessed " + s["accessed"] + ".") +
                   r" \url{" + s["url"] + "}}\n}\n")
    outputs["references.bib"] = "\n".join(bib)
    return outputs

def snapshot(book, digest, source_commit, run_url):
    pdf = ROOT / "build/main.pdf"
    assert pdf.read_bytes().startswith(b"%PDF-"), "Compiled PDF missing or invalid"
    shutil.copyfile(pdf, ROOT / "docs/glossary.pdf")
    record = {"source_sha256":digest, "content_version":book["version"],
              "pdf_sha256":hashlib.sha256(pdf.read_bytes()).hexdigest(),
              "source_commit":source_commit or None, "build_run":run_url or None}
    (ROOT / "docs/PDF-SNAPSHOT.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    prose = ("# Compiled handbook snapshot\n\nThis PDF is generated from data/handbook.json, the same source as the searchable website. "
             "All initial definitions are proposed and pending team confirmation.\n\n"
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
