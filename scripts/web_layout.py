# SPDX-License-Identifier: MIT
# Copyright (c) 2026 William Qiu
"""Static navigation shared by the generated glossary pages."""
import html
from content import ordered_terms, statements, statement_text


def esc(value):
    return html.escape(str(value), quote=True)


def search_text(book, term):
    titles = {t["slug"]: t["title"] for t in book["terms"]}
    incoming = [(owner, r) for owner in book["terms"] for r in owner["relations"] if r["target"] == term["slug"]]
    return " ".join([term["title"], term["full_name"], *term["aliases"],
        *[statement_text(s) for s in statements(term)],
        *[v["label"] + " " + v["context"] for v in term["definition_views"]],
        *[s["title"] for s in term["sections"]],
        *[row["label"] for s in term["sections"] for row in s.get("comparison", {}).get("rows", [])],
        *[link["label"] for link in term.get("reading_links", [])],
        *[r["type"] + " " + titles[r["target"]] + " " + r["condition"] for r in term["relations"]],
        *[owner["title"] + " " + r["type"] + " " + r["condition"] for owner, r in incoming],
        *term["source_gaps"], *[book["sources"][sid]["title"] for sid in term["sources"]]]).casefold()


def navigation(book, prefix="", current=""):
    items = []
    for term in ordered_terms(book):
        active = ' aria-current="page"' if term["slug"] == current else ""
        subtitle = '<span>' + esc(term["full_name"]) + '</span>' if term["full_name"] else ""
        items.append('<a class="index-item"' + active + ' data-search="' +
                     esc(search_text(book, term)) + '" href="' + prefix + 'terms/' +
                     term["slug"] + '.html">' + esc(term["title"]) + subtitle + '</a>')
    return ('<aside class="glossary-navigation" aria-label="Glossary navigation">'
            '<h2>Term index</h2><div class="search-form"><label for="search">Search the glossary</label>'
            '<div class="search-line"><input id="search" type="search" placeholder="Find a term or meaning…" '
            'autocomplete="off" aria-controls="catalog-links" aria-describedby="result-count">'
            '<button id="clear-search" type="button">Clear</button></div></div>'
            '<p id="result-count" role="status" aria-live="polite">' + str(len(items)) + ' terms</p>'
            '<p id="no-results" hidden>No terms match. Try another word or clear the search.</p>'
            '<details id="term-catalog" open><summary>Browse all terms</summary>'
            '<nav id="catalog-links" aria-label="Term index">' + ''.join(items) + '</nav></details>'
            '<div class="nav-note"><p>Working meanings, open to revision.</p><a href="' + prefix +
            'index.html#policies">Source and adoption policies</a></div>'
            '<noscript><p>Search requires JavaScript. All terms remain available in the index.</p></noscript></aside>')
