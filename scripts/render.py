# SPDX-License-Identifier: MIT
"""HTML and TeX views over one cited content model."""
import hashlib
import html
import json
from pathlib import Path
from content import ordered_terms, TIERS
from web_layout import navigation, search_text


def esc(value):
    return html.escape(str(value), quote=True)


def tex(value):
    # Standard pdfLaTeX can typeset our prose without a Unicode math/font stack.
    value = str(value).translate(str.maketrans({"→": " -> ", "·": " / ", "’": "'", "“": '"', "”": '"', "—": " -- ", "–": "-"}))
    replacements = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "&": r"\&", "#": r"\#", "_": r"\_", "%": r"\%", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(replacements.get(c, c) for c in value)


def status_label(value):
    return "Plale Lab · Proposed / not ratified" if value["status"] == "proposed" else "Plale Lab · Adopted by consensus"


def tag(value):
    return '<span class="adoption-tag ' + value["status"] + '">' + esc(status_label(value)) + '</span>'


def adoption_record(value):
    if value["status"] == "proposed":
        return 'No consensus decision recorded.'
    r = value["adoption"]
    return '<a href="' + esc(r["url"]) + '">' + esc(r["date"]) + ' unanimous decision</a><p>' + esc(r["evidence"]) + '</p>'


def blocks(t):
    """The shared page/TeX reading sequence; all cited prose traversed here."""
    result = [("scope", "Scope", [t["scope"]], False),
              ("includes", "Includes", t["includes"], True),
              ("excludes", "Excludes and counterexamples", t["excludes"], True),
              ("ambiguities", "Different usages and open boundaries", t["ambiguities"], True)]
    result += [(s["id"], s["title"], s["paragraphs"], False) for s in t["sections"]]
    result += [("operational", "Operational criteria", [t["operational"]], False),
               ("adaptation", "Lab working definition", [t["adaptation"]], False)]
    return result


def render_book(book, digest, page, source_commit="", run_url=""):
    terms = ordered_terms(book)
    by_slug = {t["slug"]: t for t in terms}
    numbers = {sid: i + 1 for i, sid in enumerate(book["sources"])}
    def citations(s, base=""):
        return '<span class="citations">' + ' '.join('<a href="' + base + '#source-' + sid + '" aria-label="Source ' + str(numbers[sid]) + ': ' + esc(book["sources"][sid]["title"]) + '">[' + str(numbers[sid]) + ']</a>' for sid in s["source_ids"]) + '</span>'
    def statement(s, base=""):
        return esc(s["text"]) + ' ' + citations(s, base) + (' <span class="inference">Editorial interpretation</span>' if s.get("inference") else '')
    def prose(items):
        return ''.join('<p>' + esc(x) + '</p>' for x in items)
    def revisions(value):
        return ''.join('<li><strong>' + esc(r["version"]) + '</strong> / ' + esc(r["date"]) + '<p>' + esc(r["text"]) + '</p></li>' for r in value["revisions"])
    def comparison(t):
        return '<div class="definition-comparison">' + ''.join('<div class="definition-view"><h3>' + esc(v["label"]) + '</h3><p class="source-context">' + esc(v["context"]) + '</p><p>' + statement(v["statement"]) + '</p></div>' for v in t["definition_views"]) + '</div>'
    all_relations = [(t, r) for t in terms for r in t["relations"]]
    def related_relations(t):
        return [(owner, r) for owner, r in all_relations if owner["slug"] == t["slug"] or r["target"] == t["slug"]]
    def term_link(slug):
        return '<a href="' + slug + '.html">' + esc(by_slug[slug]["title"]) + '</a>'
    def relationships(t):
        relations = related_relations(t)
        subtype = [(owner, r) for owner, r in relations if r["type"] == "is-a"]
        body = '<p class="section-note">Only is-a means a strict subtype. Uses and supports/orchestrates describe composition and control.</p>'
        for owner, r in subtype:
            base = '' if owner["slug"] == t["slug"] else owner["slug"] + '.html'
            body += '<ul class="subtype-tree"><li>' + term_link(r["target"]) + '<ul><li>' + term_link(owner["slug"]) + ' <span class="relation-type">is-a</span><p>' + esc(r["condition"]) + ' ' + citations(r, base) + (' <span class="inference">Editorial interpretation</span>' if r["inference"] else '') + '</p></li></ul></li></ul>'
        for owner, r in relations:
            if r["type"] == "is-a":
                continue
            base = '' if owner["slug"] == t["slug"] else owner["slug"] + '.html'
            body += '<div class="relation-row"><p>' + term_link(owner["slug"]) + ' <span class="relation-type">' + esc(r["type"]) + '</span> ' + term_link(r["target"]) + '</p><p>' + esc(r["condition"]) + ' ' + citations(r, base) + (' <span class="inference">Editorial interpretation</span>' if r["inference"] else '') + '</p></div>'
        if not relations:
            body += '<p>No relationship assertion recorded.</p>'
        return body
    def sources(t):
        output = '<ol class="source-records">'
        for sid in t["sources"]:
            s = book["sources"][sid]
            url = '../' + s["url"] if s["tier"] == 4 else s["url"]
            output += '<li id="source-' + sid + '" value="' + str(numbers[sid]) + '"><a href="' + esc(url) + '">' + esc(s["title"]) + '</a><p>' + esc(s["author"]) + '. <span class="source-tier">Tier ' + str(s["tier"]) + ' / ' + esc(s["kind"]) + '</span></p><p>' + esc(s["version"]) + '. ' + esc(s["locator"]) + '. Accessed ' + esc(s["accessed"]) + '.</p><p>Context: ' + esc(s["context"]) + '</p><p>Verification: ' + esc(s["verification"]) + '</p></li>'
        return output + '</ol>'

    rows = ''.join('<article class="term-row" data-search="' + esc(search_text(book, t)) + '"><h3><a class="term-name" href="terms/' + t["slug"] + '.html">' + esc(t["title"]) + '</a></h3><p class="full-name">' + esc(t["full_name"]) + '</p><p>' + statement(t["definition"], 'terms/' + t["slug"] + '.html') + '</p></article>' for t in terms)
    index = '<section class="intro"><div><h1>Shared glossary</h1><p class="lead">' + esc(book["introduction"][0]) + '</p><p class="notice">Definitions with boundaries, evidence and an explicit Lab proposal.</p></div><aside class="editor-note"><h2>An evolving reference</h2><p>' + str(len(terms)) + ' terms. Several meanings. A clearer working vocabulary.</p><a href="#policies">How we use sources</a></aside></section><div class="index-heading"><h2>Browse definitions</h2></div><div id="term-index" class="curated-index">' + rows + '</div><section class="policy" id="policies"><h2>About this glossary</h2>' + prose(book["introduction"][1:]) + '<h2>How we choose meanings</h2>' + prose(book["source_policy"]) + '<h3>Lab adoption</h3><p>' + tag(book["lab_guide"]) + '</p><p>' + esc(book["adoption_policy"]) + '</p><p><a href="lab-guide.html">Read the versioned internal proposal</a></p></section>'
    outputs = {"docs/index.html": page(book, "Index", index, digest, source_commit=source_commit, run_url=run_url, sidebar=navigation(book))}
    for t in terms:
        sections = []
        for sid, heading, items, listed in blocks(t):
            inner = '<ul>' + ''.join('<li>' + statement(s) + '</li>' for s in items) + '</ul>' if listed else ''.join('<p>' + statement(s) + '</p>' for s in items)
            if sid == "adaptation":
                inner = '<p>' + tag(t) + '</p>' + inner + '<p class="section-note">' + adoption_record(t) + '</p>'
            sections.append('<section id="' + sid + '"><h2>' + heading + '</h2>' + inner + '</section>')
        # Comparisons follow the definition; typed relations precede the internal proposal.
        sections.insert(0, '<section id="definitions"><h2>Definition comparison</h2>' + comparison(t) + '</section>')
        sections.insert(-1, '<section id="relations"><h2>Concept relationships</h2>' + relationships(t) + '</section>')
        contents = [("definitions", "Definition comparison")] + [(sid, heading) for sid, heading, _, _ in blocks(t) if sid != "adaptation"] + [("relations", "Concept relationships"), ("adaptation", "Lab working definition"), ("sources", "Sources & gaps"), ("revisions", "Revision record")]
        related = ''.join('<a href="' + slug + '.html">' + esc(by_slug[slug]["title"]) + '</a>' for slug in t["related"])
        mobile_toc = '<details class="mobile-contents"><summary>On this page</summary><nav aria-label="Mobile page contents">' + ''.join('<a href="#' + sid + '">' + heading + '</a>' for sid, heading in contents) + '</nav></details>'
        body = '<a class="back" href="../index.html">Back to glossary</a><div class="term-layout"><article><h1 class="term-title">' + esc(t["title"]) + '</h1><p class="subtitle">' + esc(t["full_name"]) + '</p><p class="lead">' + statement(t["definition"]) + '</p>' + mobile_toc + ''.join(sections) + '<section class="sources" id="sources"><h2>Sources and research gaps</h2><div class="source-gaps"><h3>Research notes</h3>' + prose(t["source_gaps"]) + '</div>' + sources(t) + '</section><section id="revisions"><h2>Revision record</h2><ol class="revision-list">' + revisions(t) + '</ol></section></article><aside class="entry-record"><nav class="contents" aria-label="On this page"><h2>On this page</h2>' + ''.join('<a href="#' + sid + '">' + heading + '</a>' for sid, heading in contents) + '</nav><h2>Related terms</h2><nav aria-label="Related terms">' + related + '</nav><h2>Entry record</h2><p>Version ' + esc(t["entry_version"]) + '<br>Updated ' + esc(t["updated"]) + '</p><p>Lab definition: ' + esc(t["status"]) + '</p><a href="../lab-guide.html">Internal proposal</a></aside></div>'
        outputs['docs/terms/' + t["slug"] + '.html'] = page(book, t["title"], body, digest, '../', source_commit, run_url, sidebar=navigation(book, '../', t["slug"]))
    guide = book["lab_guide"]
    body = '<a class="back" href="index.html">Back to glossary</a><article class="lab-guide"><h1>' + esc(guide["title"]) + '</h1><p class="lead">A versioned internal proposal, open for discussion.</p><p>' + tag(guide) + '</p><p>Version ' + esc(guide["version"]) + ' / Updated ' + esc(guide["updated"]) + '</p><p>' + adoption_record(guide) + '</p>' + ''.join('<section id="' + section["id"] + '"><h2>' + esc(section["title"]) + '</h2>' + prose(section["paragraphs"]) + '</section>' for section in guide["sections"]) + '<section id="revisions"><h2>Revision record</h2><ol>' + revisions(guide) + '</ol></section></article>'
    outputs['docs/lab-guide.html'] = page(book, 'Lab guide', body, digest, source_commit=source_commit, run_url=run_url, sidebar=navigation(book))
    outputs['docs/.nojekyll'] = ''
    outputs['docs/BUILD-INFO.json'] = json.dumps(dict(content_version=book['version'], updated=book['updated'], source='data/handbook.json', source_sha256=digest, terms=len(terms), display_order=book['display_order'], source_commit=source_commit or None, build_run=run_url or None), indent=2) + '\n'
    latex = [r'\documentclass[11pt,letterpaper]{article}', r'\usepackage[T1]{fontenc}', r'\usepackage[utf8]{inputenc}', r'\usepackage{lmodern}', r'\usepackage[margin=1in]{geometry}', r'\usepackage{microtype}', r'\usepackage{xcolor}', r'\usepackage{hyperref}', r'\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue,citecolor=blue}', r'\pdfinfoomitdate=1', r'\pdftrailerid{}', r'\Urlmuskip=0mu plus 1mu', r'\setlength{\parindent}{0pt}', r'\setlength{\parskip}{0.45em}', r'\definecolor{proposal}{HTML}{765400}', r'\definecolor{adopted}{HTML}{145D32}', '% Generated from data/handbook.json; do not edit.', r'\begin{document}', r'\section*{' + tex(book['title']) + '}', tex('Version ' + book['version'] + ' / ' + book['updated']), *[tex(x) + '\n' for x in book['introduction']], r'\subsection*{Source policy}', *[tex(x) + '\n' for x in book['source_policy']], r'\subsection*{Lab adoption}', tex(book['adoption_policy']), r'\subsection*{Licensing}', tex(book['license']), r'\newpage\section*{Reading index}', r'\begin{itemize}']
    latex += [r'\item \hyperlink{term-' + t['slug'] + '}{' + tex(t['title']) + '}' for t in terms] + [r'\end{itemize}']
    def cited(s):
        return tex(s.get('text', s.get('condition'))) + r' \cite{' + ','.join(s['source_ids']) + '}' + (r' \textit{Editorial interpretation.}' if s.get('inference') else '')
    for t in terms:
        latex += [r'\newpage\hypertarget{term-' + t['slug'] + '}{}', r'\section*{' + tex(t['title']) + '}', tex(t['full_name']), cited(t['definition']), r'\subsection*{Definition comparison}']
        for v in t['definition_views']:
            latex += [r'\subsubsection*{' + tex(v['label']) + '}', tex(v['context']), cited(v['statement'])]
        for sid, heading, items, listed in blocks(t):
            if sid == 'adaptation':
                latex += [r'\subsection*{Concept relationships}', tex('Only is-a means a strict subtype. Uses and supports/orchestrates describe composition and control.')]
                for owner, r in related_relations(t):
                    latex += [tex(owner['title'] + ' ' + r['type'] + ' ' + by_slug[r['target']]['title']) + r'\par ' + cited(r)]
            latex.append(r'\subsection*{' + tex(heading) + '}')
            if sid == 'adaptation':
                latex.append(r'\textcolor{' + ('proposal' if t['status'] == 'proposed' else 'adopted') + '}{' + tex(status_label(t)) + '}')
                if t['status'] == 'adopted':
                    latex += [tex(t['adoption']['date'] + ' / ' + t['adoption']['evidence']), r'\url{' + t['adoption']['url'] + '}']
                else:
                    latex.append('No consensus decision recorded.')
            if listed:
                latex += [r'\begin{itemize}', *[r'\item ' + cited(s) for s in items], r'\end{itemize}']
            else:
                latex += [cited(s) + '\n' for s in items]
        latex += [r'\subsection*{Sources and research gaps}', *[tex(x) + '\n' for x in t['source_gaps']]]
        for sid in t['sources']:
            s = book['sources'][sid]
            latex += [r'\cite{' + sid + '} ' + tex('Tier ' + str(s['tier']) + ' / ' + s['kind'] + '. Context: ' + s['context'] + ' Verification: ' + s['verification'])]
        latex += [r'\subsection*{Revision record}', tex('Version ' + t['entry_version'] + ' / Updated ' + t['updated']), *[tex(r['version'] + ' / ' + r['date'] + ': ' + r['text']) for r in t['revisions']], r'\subsection*{Related terms}', '; '.join(r'\hyperlink{term-' + slug + '}{' + tex(by_slug[slug]['title']) + '}' for slug in t['related'])]
    latex += [r'\newpage\hypertarget{lab-guide}{}', r'\section*{' + tex(guide['title']) + '}', tex('Version ' + guide['version'] + ' / ' + guide['updated']), r'\textcolor{' + ('proposal' if guide['status'] == 'proposed' else 'adopted') + '}{' + tex(status_label(guide)) + '}']
    if guide['status'] == 'adopted':
        latex += [tex(guide['adoption']['date'] + ' / ' + guide['adoption']['evidence']), r'\url{' + guide['adoption']['url'] + '}']
    else:
        latex.append('No consensus decision recorded.')
    for section in guide['sections']:
        latex += [r'\subsection*{' + tex(section['title']) + '}', *[tex(x) + '\n' for x in section['paragraphs']]]
    latex += [r'\subsection*{Revision record}', *[tex(r['version'] + ' / ' + r['date'] + ': ' + r['text']) for r in guide['revisions']], r'\newpage\section*{Build provenance}', r'Source content SHA-256: \nolinkurl{' + digest + '}.']
    if source_commit:
        latex.append(r'Source commit: \nolinkurl{' + source_commit + '}.')
    if run_url:
        latex.append(r'Build run: \url{' + run_url + '}.')
    latex += [r'\bibliographystyle{plain}', r'\bibliography{references}', r'\end{document}']
    outputs['main.tex'] = '\n'.join(latex) + '\n'
    bib = []
    for sid, s in book['sources'].items():
        url = s['url']
        note = s['version'] + '. ' + s['locator'] + '. Accessed ' + s['accessed'] + '.'
        bib.append('@misc{' + sid + ',\n  author = {{' + tex(s['author']) + '}},\n  title = {{' + tex(s['title']) + '}},\n  year = {' + s['year'] + '},\n  howpublished = {' + tex(s['kind']) + '},\n  note = {' + tex(note) + (r' \hyperlink{lab-guide}{Internal proposal reproduced in this edition}' if s['tier'] == 4 else r' \url{' + url + '}') + '}\n}\n')
    outputs['references.bib'] = '\n'.join(bib)
    return outputs
