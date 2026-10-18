# SPDX-License-Identifier: MIT
"""Shared content traversal and semantic validation; no rendering or network I/O."""
from datetime import date
import re
from urllib.parse import urlsplit

TIERS = {1: "Institutional definition", 2: "Peer-reviewed paper",
         3: "Industry / first-party / preprint / academic", 4: "Repository internal proposal"}
RELATIONS = {"is-a", "uses", "supports/orchestrates"}
KINDS = {"process", "runtime", "model", "system", "property"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def secure_url(value):
    if not isinstance(value, str):
        return False
    u = urlsplit(value)
    return u.scheme == "https" and bool(u.hostname) and not u.username and not u.password and not any(c.isspace() or c in '{}\\' for c in value)


def iso_date(value):
    try:
        return isinstance(value, str) and date.fromisoformat(value).isoformat() == value
    except (TypeError, ValueError):
        return False


def ordered_terms(book):
    by_slug = {t["slug"]: t for t in book["terms"]}
    return [by_slug[slug] for slug in book["display_order"]]


PAGE_SECTIONS = {"scope", "includes", "excludes", "ambiguities", "definitions", "operational", "relations", "adaptation", "sources", "revisions"}


def statements(value):
    """Yield each cited statement exactly once, including relation conditions."""
    if isinstance(value, dict):
        if "source_ids" in value:
            yield value
        for key, child in value.items():
            if key != "source_ids":
                yield from statements(child)
    elif isinstance(value, list):
        for child in value:
            yield from statements(child)


def statement_text(value):
    return value.get("text", value.get("condition", ""))


def adoption(value, label):
    require(value.get("status") in {"proposed", "adopted"}, label + ": invalid status")
    if value["status"] == "adopted":
        record = value.get("adoption") or {}
        require(record.get("consensus") == "unanimous" and nonempty(record.get("evidence")), label + ": adoption requires unanimous consensus evidence")
        require(iso_date(record.get("date")) and secure_url(record.get("url")), label + ": adoption requires date and accessible HTTPS decision link")
    else:
        require(value.get("adoption") is None, label + ": proposed status cannot carry an adoption decision")


def validate(book):
    require(book.get("schema_version") == 2, "Expected schema_version 2")
    terms, sources = book["terms"], book["sources"]
    by_slug = {t["slug"]: t for t in terms}
    require(len(by_slug) == len(terms) and len(terms) > 0, "Duplicate or empty term collection")
    order = book.get("display_order", [])
    require(len(order) == len(set(order)) == len(terms) and set(order) == set(by_slug), "display_order must contain each active slug exactly once")
    guide = book["lab_guide"]
    adoption(guide, "Repository guide")
    require(nonempty(guide.get("id")) and nonempty(guide.get("version")) and iso_date(guide.get("updated")), "Repository guide version required")
    section_ids = set()
    for section in guide["sections"]:
        require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", section["id"]) and section["id"] not in section_ids, "Invalid or duplicate guide section")
        section_ids.add(section["id"])
        require(nonempty(section["title"]) and section["paragraphs"] and all(nonempty(x) for x in section["paragraphs"]), "Empty guide section")
    for sid, source in sources.items():
        require(bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", sid)), "Invalid source ID")
        require(type(source.get("tier")) is int and source["tier"] in TIERS, sid + ": invalid source tier")
        for key in ("title", "author", "year", "kind", "version", "locator", "context", "verification"):
            require(nonempty(source.get(key)), sid + ": missing " + key)
        require(bool(re.fullmatch(r"\d{4}", source["year"])) and iso_date(source.get("accessed")), sid + ": invalid source dates")
        if source["tier"] == 4:
            require(source.get("guide_id") == guide["id"] and source["url"] == "lab-guide.html", sid + ": unresolved internal reference")
            require(guide["version"] in source["version"], sid + ": internal reference version mismatch")
        else:
            require(secure_url(source.get("url")), sid + ": source URL must be HTTPS")
    graph = {slug: [] for slug in by_slug}
    for t in terms:
        slug = t["slug"]
        require(bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug)), "Invalid term slug")
        for key in ("title", "entry_version"):
            require(nonempty(t.get(key)), slug + ": missing " + key)
        require(t.get("concept_kind") in KINDS and iso_date(t.get("updated")), slug + ": invalid kind or update date")
        adoption(t, slug)
        for key in ("definition", "scope", "operational", "adaptation"):
            require(isinstance(t.get(key), dict) and "text" in t[key] and "source_ids" in t[key], slug + ": missing cited " + key)
        for key in ("includes", "excludes", "ambiguities"):
            require(isinstance(t.get(key), list) and t[key] and all(isinstance(x, dict) and "text" in x and "source_ids" in x for x in t[key]), slug + ": missing cited " + key)
        require(t.get("definition_views"), slug + ": missing definition comparison")
        for view in t["definition_views"]:
            require(nonempty(view.get("label")) and nonempty(view.get("context")) and isinstance(view.get("statement"), dict) and "source_ids" in view["statement"], slug + ": invalid definition comparison")
        require(t.get("source_gaps") and all(nonempty(x) for x in t["source_gaps"]), slug + ": source audit/gaps required")
        require(set(t["related"]) <= set(by_slug) and slug not in t["related"], slug + ": unknown related term")
        for link in t.get("reading_links", []):
            require(isinstance(link, dict), slug + ": invalid reading link")
            target = by_slug.get(link.get("target"))
            require(target is not None and nonempty(link.get("label")), slug + ": invalid reading link")
            targets = PAGE_SECTIONS | {s["id"] for s in target["sections"]}
            require(link.get("section") in targets, slug + ": unknown reading-link section")
        used = set()
        for statement in statements(t):
            require(nonempty(statement_text(statement)), slug + ": empty statement")
            ids = statement["source_ids"]
            require(isinstance(ids, list) and ids and len(ids) == len(set(ids)) and set(ids) <= set(sources), slug + ": missing or unknown citation")
            require(type(statement.get("inference", False)) is bool, slug + ": inference must be boolean")
            used.update(ids)
        require(set(t["sources"]) == used and len(t["sources"]) == len(used), slug + ": source list differs from inline citations")
        tiers = [sources[sid]["tier"] for sid in t["sources"]]
        require(tiers == sorted(tiers), slug + ": source list must follow research tier order")
        require(any(sources[sid]["tier"] < 4 for sid in t["definition"]["source_ids"]), slug + ": core definition needs applicable external evidence")
        require(any(sources[sid]["tier"] == 4 for sid in t["adaptation"]["source_ids"]), slug + ": Repository meaning needs internal proposal citation")
        for r in t["relations"]:
            require(r.get("target") in by_slug and r["target"] != slug and r.get("type") in RELATIONS, slug + ": invalid relation target/type")
            require("source_ids" in r and type(r.get("inference")) is bool and nonempty(r.get("condition")), slug + ": relation needs condition, attribution and inference flag")
            if r["type"] == "is-a":
                require(t["concept_kind"] == by_slug[r["target"]]["concept_kind"], slug + ": is-a cannot cross semantic kinds; use a component or orchestration relation")
                require(any(sources[sid]["tier"] < 4 for sid in r["source_ids"]), slug + ": is-a needs external evidence")
                graph[slug].append(r["target"])
        ids = set()
        for section in t["sections"]:
            require(nonempty(section.get("id")) and section["id"] not in ids and section["id"] not in PAGE_SECTIONS, slug + ": duplicate/reserved section ID")
            require(bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", section["id"])) and nonempty(section.get("title")), slug + ": invalid section")
            require(section.get("paragraphs") and all(isinstance(p, dict) and "source_ids" in p and "text" in p for p in section["paragraphs"]), slug + ": missing section citations")
            if "comparison" in section:
                comparison = section["comparison"]
                require(isinstance(comparison, dict) and all(nonempty(comparison.get(k)) for k in ("left_title", "right_title")), slug + ": invalid paired comparison")
                require(isinstance(comparison.get("rows"), list) and comparison["rows"], slug + ": empty paired comparison")
                for row in comparison["rows"]:
                    require(isinstance(row, dict) and nonempty(row.get("label")) and all(isinstance(row.get(k), dict) and "text" in row[k] and "source_ids" in row[k] for k in ("left", "right")), slug + ": comparison cells need citations")
            ids.add(section["id"])
        require(t.get("revisions"), slug + ": revision record required")
        for r in t["revisions"]:
            require(nonempty(r.get("version")) and iso_date(r.get("date")) and nonempty(r.get("text")), slug + ": invalid revision")
    seen, visiting = set(), set()
    def visit(slug):
        require(slug not in visiting, "is-a cycle detected")
        if slug in seen:
            return
        visiting.add(slug)
        for target in graph[slug]:
            visit(target)
        visiting.remove(slug)
        seen.add(slug)
    for slug in graph:
        visit(slug)
