# SPDX-License-Identifier: MIT
# Copyright (c) 2026 William Qiu
"""Content and navigation regressions for the static website."""
import copy
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import posixpath
import sys
import unittest
from urllib.parse import urlsplit

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate import generate, validate
from web_layout import search_text


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids, self.links, self.text, self.elements = [], [], [], []
        self.feed(source)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        self.elements.append((tag, attrs))
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a":
            self.links.append(attrs["href"])

    def handle_data(self, data):
        self.text.append(data)


class WebsiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = (ROOT / "data/handbook.json").read_bytes()
        cls.book = json.loads(raw)
        cls.digest = hashlib.sha256(raw).hexdigest()
        validate(cls.book)
        cls.outputs = generate(cls.book, cls.digest)

    def test_active_routes_and_reading_order(self):
        order = ["workflow", "harness", "model", "llm", "agent", "schema"]
        self.assertEqual(self.book["display_order"], order)
        routes = {path for path in self.outputs if path.startswith("docs/terms/")}
        self.assertEqual(routes, {"docs/terms/" + slug + ".html" for slug in order})
        doc = Document(self.outputs["docs/index.html"])
        catalog = [attrs["href"] for _, attrs in doc.elements if attrs.get("class") == "index-item"]
        self.assertEqual(catalog, ["terms/" + slug + ".html" for slug in order])
        for slug in ["ai", "ml", "foundation-model", "generative-ai", "ai-engineering", "provenance"]:
            self.assertNotIn("terms/" + slug + ".html", self.outputs["docs/index.html"])
        tex_output = self.outputs["main.tex"]
        positions = [tex_output.index("\\hypertarget{term-" + slug + "}") for slug in order]
        self.assertEqual(positions, sorted(positions))

    def test_every_local_page_and_fragment_resolves(self):
        documents = {path: Document(value) for path, value in self.outputs.items() if path.endswith(".html")}
        for path, doc in documents.items():
            self.assertEqual(len(doc.ids), len(set(doc.ids)), path)
            for href in doc.links:
                link = urlsplit(href)
                if link.scheme or link.netloc or link.path.endswith(".pdf"):
                    continue
                target = posixpath.normpath(str(PurePosixPath(path).parent / link.path)) if link.path else path
                self.assertIn(target, documents, (path, href))
                if link.fragment:
                    self.assertIn(link.fragment, documents[target].ids, (path, href))

    def test_all_cited_prose_html_tex_parity_and_no_js_reading(self):
        from content import statements, statement_text
        from render import tex
        for term in self.book["terms"]:
            doc = Document(self.outputs["docs/terms/" + term["slug"] + ".html"])
            text = "".join(doc.text)
            for st in statements(term):
                self.assertIn(statement_text(st), text)
                self.assertIn(tex(statement_text(st)), self.outputs["main.tex"])
                self.assertIn("\\cite{" + ",".join(st["source_ids"]) + "}", self.outputs["main.tex"])
            for source_id in term["sources"]:
                self.assertIn("source-" + source_id, doc.ids)
                self.assertIn("@misc{" + source_id, self.outputs["references.bib"])
                source = self.book["sources"][source_id]
                self.assertIn("../" + source["url"] if source["tier"] == 4 else source["url"], doc.links)
            for related in term["related"]:
                self.assertIn(related + ".html", doc.links)
            active = [a for _, a in doc.elements if a.get("aria-current") == "page"]
            self.assertEqual([a["href"] for a in active], ["../terms/" + term["slug"] + ".html"])
            self.assertIn("Plale Lab · Proposed / not ratified", text)
            self.assertNotIn("Plale Lab · Adopted by consensus", text)
            self.assertIn("No consensus decision recorded.", text)
        guide = "".join(Document(self.outputs["docs/lab-guide.html"]).text)
        for section in self.book["lab_guide"]["sections"]:
            for p in section["paragraphs"]:
                self.assertIn(p, guide)
                self.assertIn(tex(p), self.outputs["main.tex"])

    def test_search_covers_comparisons_and_relationships(self):
        for term in self.book["terms"]:
            text = search_text(self.book, term)
            for view in term["definition_views"]:
                self.assertIn(view["statement"]["text"].casefold(), text)
                self.assertIn(view["context"].casefold(), text)
            for rel in term["relations"]:
                self.assertIn(rel["condition"].casefold(), text)
                self.assertIn(rel["type"].casefold(), text)
            for alias in term["aliases"]:
                self.assertIn(alias.casefold(), text)
            for owner in self.book["terms"]:
                for rel in owner["relations"]:
                    if rel["target"] == term["slug"]:
                        self.assertIn(owner["title"].casefold(), text)
                        self.assertIn(rel["condition"].casefold(), text)
        for query in ["artificial intelligence engineering", "foundation model", "machine learning system"]:
            self.assertFalse(any(query in search_text(self.book, t) for t in self.book["terms"]), query)

    def test_escaping_and_evidenced_adoption(self):
        b = copy.deepcopy(self.book)
        t = b["terms"][0]
        hostile = '<script>alert("x")</script> & research {test} %'
        t["definition"]["text"] = hostile
        t["status"] = "adopted"
        t["adoption"] = {"date": "2026-10-10", "url": "https://example.org/decision?a=1&b=2", "consensus": "unanimous", "evidence": "Synthetic test fixture: unanimous decision for this scope."}
        validate(b)
        out = generate(b, self.digest)
        doc = Document(out["docs/terms/workflow.html"])
        self.assertNotIn('<script>alert', out["docs/terms/workflow.html"])
        self.assertIn(hostile, "".join(doc.text))
        self.assertIn(t["adoption"]["url"], doc.links)
        self.assertIn("Plale Lab · Adopted by consensus", "".join(doc.text))
        self.assertIn('class="adoption-tag adopted"', out["docs/terms/workflow.html"])
        self.assertIn("\\{test\\}", out["main.tex"])

    def test_reject_missing_and_unknown_citations(self):
        for ids in [[], ["does-not-exist"]]:
            b = copy.deepcopy(self.book); b["terms"][0]["definition"]["source_ids"] = ids
            with self.assertRaisesRegex(ValueError, "citation"):
                validate(b)
        b = copy.deepcopy(self.book); del b["terms"][0]["scope"]["source_ids"]
        with self.assertRaisesRegex(ValueError, "cited scope"):
            validate(b)

    def test_reject_unknown_relationship_and_internal_page(self):
        for key, value in [("target", "missing"), ("type", "nested-in")]:
            b = copy.deepcopy(self.book);b["terms"][1]["relations"][0][key] = value
            with self.assertRaisesRegex(ValueError, "relation"):
                validate(b)
        b=copy.deepcopy(self.book);b["sources"]["lab-guide-v1"]["url"]="missing.html"
        with self.assertRaisesRegex(ValueError, "internal reference"):
            validate(b)

    def test_skill_scenario_wrong_nesting(self):
        b=copy.deepcopy(self.book);b["terms"][1]["relations"][0]["type"]="is-a"
        with self.assertRaisesRegex(ValueError, "semantic kinds"):
            validate(b)
        b=copy.deepcopy(self.book);b["terms"][4]["relations"][0]["type"]="is-a"
        with self.assertRaisesRegex(ValueError, "semantic kinds"):
            validate(b)

    def test_is_a_cycle_rejected(self):
        b=copy.deepcopy(self.book)
        b["terms"][2]["relations"].append({"target":"llm","type":"is-a","condition":"Synthetic reverse edge to exercise cycle detection.","source_ids":["eu-us-ai"],"inference":True})
        with self.assertRaisesRegex(ValueError, "cycle"):
            validate(b)

    def test_skill_scenario_green_without_consensus(self):
        for decision in [None, {"date":"2026-10-10","url":"https://example.org/merge"}, {"date":"2026-10-10","url":"https://example.org/decision","consensus":"majority","evidence":"A majority vote."}]:
            b=copy.deepcopy(self.book);b["terms"][0].update(status="adopted",adoption=decision)
            with self.assertRaisesRegex(ValueError, "consensus evidence"):
                validate(b)
        b=copy.deepcopy(self.book);b["lab_guide"].update(status="adopted",adoption=None)
        with self.assertRaisesRegex(ValueError, "consensus evidence"):
            validate(b)

    def test_skill_scenario_add_new_entry(self):
        b=copy.deepcopy(self.book)
        # Forward scenario: an editor adds a related process without modifying renderers.
        new=copy.deepcopy(b["terms"][0]);new.update(slug="research-workflow",title="Research workflow",relations=[],related=["workflow"])
        from content import statements
        used={sid for st in statements(new) for sid in st["source_ids"]}
        new["sources"]=[sid for sid in new["sources"] if sid in used]
        b["terms"].append(new);b["display_order"].append(new["slug"])
        validate(b)
        out=generate(b,self.digest)
        self.assertIn("docs/terms/research-workflow.html",out)
        self.assertIn("Research workflow",out["main.tex"])
        count = len(self.book["terms"]) + 1
        self.assertIn(f"{count} terms. Several meanings.",out["docs/index.html"])
        self.assertEqual(len([a for _,a in Document(out["docs/index.html"]).elements if a.get("class")=="index-item"]),count)

    def test_schema_instance_and_extraction_boundaries(self):
        term = next(t for t in self.book["terms"] if t["slug"] == "schema")
        self.assertEqual(term["status"], "proposed")
        self.assertIsNone(term["adoption"])
        self.assertEqual([self.book["sources"][s]["tier"] for s in term["sources"]], [1, 2, 3, 3, 4])
        doc = Document(self.outputs["docs/terms/schema.html"])
        text = "".join(doc.text)
        self.assertIn('schema-extraction', doc.ids)
        self.assertIn('a data instance', text)
        self.assertIn('meta-schema', text)
        self.assertIn('Schema extraction is the process', text)
        self.assertIn('does not by itself establish', text)
        self.assertIn('Internet-Draft', text)
        self.assertIn('schema extraction', search_text(self.book, term))
        self.assertIn('model.html', doc.links)
        self.assertIn('workflow.html', doc.links)

    def test_skill_scenario_source_gap_is_visible(self):
        b=copy.deepcopy(self.book);b["terms"][1]["source_gaps"]=["No directly applicable final institutional standard established in this review; retain attributed engineering usage."]
        validate(b)
        out=generate(b,self.digest)
        self.assertIn(b["terms"][1]["source_gaps"][0],"".join(Document(out["docs/terms/harness.html"]).text))

    def test_preview_prunes_retired_pages_and_labels_pdf(self):
        from preview import prepare
        target=ROOT / "build/preview/terms/retired-test.html"
        target.parent.mkdir(parents=True,exist_ok=True);target.write_text("Synthetic retired route",encoding="utf-8")
        preview=prepare()
        self.assertFalse(target.exists())
        html=(preview / "index.html").read_text(encoding="utf-8")
        record=json.loads((ROOT / "docs/PDF-SNAPSHOT.json").read_text(encoding="utf-8"))
        self.assertIn("Previous PDF · v"+record["content_version"],html)
        self.assertIn("does not match this glossary edition",html)
        self.assertEqual(hashlib.sha256((preview / "previous-glossary.pdf").read_bytes()).hexdigest(),record["pdf_sha256"])

    def test_adoption_colors_have_text_contrast(self):
        import re
        css=(ROOT / "docs/assets/style.css").read_text(encoding="utf-8")
        def luminance(color):
            channels=[int(color[i:i+2],16)/255 for i in (1,3,5)]
            linear=[c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4 for c in channels]
            return sum(c*w for c,w in zip(linear,[0.2126,0.7152,0.0722]))
        palettes=re.findall(r"--proposed-ink:(#[0-9a-f]+);--proposed-paper:(#[0-9a-f]+);--adopted-ink:(#[0-9a-f]+);--adopted-paper:(#[0-9a-f]+)",css)
        self.assertGreaterEqual(len(palettes),2)
        for palette in palettes:
            for fg,bg in [palette[:2],palette[2:]]:
                low,high=sorted([luminance(fg),luminance(bg)])
                self.assertGreaterEqual((high+0.05)/(low+0.05),4.5,(fg,bg))

    def test_skill_template_and_schema_stay_in_sync(self):
        skill=ROOT / ".agents/skills/plalelab-glossry-edit"
        self.assertEqual((ROOT / "templates/definition-entry.json").read_bytes(),(skill / "assets/definition-entry.json").read_bytes())
        schema=json.loads((skill / "references/content-schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schema_version"]["const"],self.book["schema_version"])
        self.assertIn("consensus",schema["$defs"]["adoption"]["required"])
        entry=json.loads((skill / "assets/definition-entry.json").read_text(encoding="utf-8"))
        self.assertEqual(entry["status"],"proposed")
        self.assertIsNone(entry["adoption"])


if __name__ == "__main__":
    unittest.main()
