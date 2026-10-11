---
name: Plale Lab Glossary
description: A searchable research reference on warm paper with green ink and editorial
  reading typography.
colors:
  paper: '#f8f7f1'
  ink: '#213b33'
  muted: '#5e6c63'
  accent: '#225b44'
  wash: '#ecefe6'
  line: '#d5dad0'
  paper-dark: '#18241f'
  ink-dark: '#eef2ea'
  muted-dark: '#b4c4b8'
  accent-dark: '#aed6b5'
  wash-dark: '#24362b'
  line-dark: '#415449'
  proposed-ink: '#6b4b00'
  proposed-paper: '#fff0bc'
  adopted-ink: '#175634'
  adopted-paper: '#e5f1e9'
  proposed-ink-dark: '#f3d685'
  proposed-paper-dark: '#433719'
  adopted-ink-dark: '#c4eccf'
  adopted-paper-dark: '#1c3b29'
typography:
  display:
    fontFamily: Newsreader, Georgia, serif
    fontSize: clamp(44px, 4.8vw, 64px)
    fontWeight: 500
    lineHeight: 1.07
    letterSpacing: -.025em
  definition:
    fontFamily: Newsreader, Georgia, serif
    fontSize: 28px
    fontWeight: 400
    lineHeight: 1.6
  term-title:
    fontFamily: Newsreader, Georgia, serif
    fontSize: 29px
    fontWeight: 500
    lineHeight: 1.2
  headline:
    fontFamily: Manrope, system-ui, sans-serif
    fontSize: 16px
    fontWeight: 650
    lineHeight: 1.4
  body:
    fontFamily: Manrope, system-ui, sans-serif
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.9
  navigation:
    fontFamily: Manrope, system-ui, sans-serif
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.7
  label:
    fontFamily: Manrope, system-ui, sans-serif
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.8
  annotation:
    fontFamily: Manrope, system-ui, sans-serif
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.9
  summary:
    fontFamily: Manrope, system-ui, sans-serif
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.85
  relation-label:
    fontFamily: Manrope, system-ui, sans-serif
    fontSize: 13px
    fontWeight: 500
    lineHeight: 1.7
  adoption-label:
    fontFamily: Manrope, system-ui, sans-serif
    fontSize: 13px
    fontWeight: 600
    lineHeight: 1.7
  page-directory:
    fontFamily: Manrope, system-ui, sans-serif
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.8
rounded:
  control: 2px
spacing:
  paragraph: 14px
  compact-gutter: 20px
  mobile-gutter: 21px
  group: 24px
  tablet-gutter: 32px
  article-section: 38px
  desktop-gutter: 48px
components:
  appearance-button:
    backgroundColor: transparent
    textColor: '{colors.ink}'
    rounded: '{rounded.control}'
    padding: 7px 12px
  search-field:
    backgroundColor: '{colors.paper}'
    textColor: '{colors.ink}'
    rounded: '{rounded.control}'
    padding: 8px 10px
  navigation-item:
    backgroundColor: transparent
    textColor: '{colors.ink}'
    rounded: '{rounded.control}'
    padding: 11px 10px
    typography: '{typography.navigation}'
  navigation-item-hover:
    backgroundColor: '{colors.wash}'
    textColor: '{colors.ink}'
    rounded: '{rounded.control}'
    padding: 11px 10px
    typography: '{typography.navigation}'
  navigation-item-current:
    backgroundColor: '{colors.wash}'
    textColor: '{colors.accent}'
    rounded: '{rounded.control}'
    padding: 11px 10px
  comparison-row:
    backgroundColor: transparent
    textColor: '{colors.ink}'
    padding: 18px 0 5px
  relation-row:
    backgroundColor: transparent
    textColor: '{colors.ink}'
    padding: 16px 0 1px
  page-directory:
    backgroundColor: transparent
    textColor: '{colors.ink}'
    padding: 12px 0
    typography: '{typography.annotation}'
  adoption-proposed:
    backgroundColor: '{colors.proposed-paper}'
    textColor: '{colors.proposed-ink}'
    rounded: '{rounded.control}'
    padding: 4px 8px
    typography: '{typography.adoption-label}'
  adoption-adopted:
    backgroundColor: '{colors.adopted-paper}'
    textColor: '{colors.adopted-ink}'
    rounded: '{rounded.control}'
    padding: 4px 8px
    typography: '{typography.adoption-label}'
---

# Design System: Plale Lab Glossary

## Overview

**Creative North Star: "The searchable research reference"**

The approved fusion combines B's persistent searchable navigation with A's editorial reading layout. Warm paper, green ink and generous paragraph rhythm support finding a meaning quickly, then reading its scope, boundaries and sources carefully. This records the built static glossary rather than the comparison prototype's routing or provisional details.

Navigation uses Manrope, a stable index and an explicit current term. Newsreader gives titles, term rows and definitions a publication character. Neutral comparison rows make competing definitions and their evidence visible; compact semantic tags distinguish the Lab proposal from documented adoption. Light and dark appearances share the same hierarchy; no animation or authored transition is applied.

**Key Characteristics:**

- Persistent searchable index paired with a flexible reading column.
- Warm neutral surfaces, dark green ink and restrained green links.
- Newsreader for reading landmarks; Manrope for navigation and ordinary prose.
- Flat surfaces with tonal selection and thin structural dividers.
- Static term addresses and native HTML enhanced by local search.

## Colors

Internal adoption uses compact text tags with the frontmatter's proposed and adopted ink/paper pairs. Yellow identifies an unratified Lab proposal; green identifies a recorded consensus decision. All current definitions remain proposed. External source tiers and editorial interpretation labels stay neutral.

The frontmatter records the stylesheet's exact light and dark palette. Source names map directly to CSS custom properties; the dark variants replace the corresponding six roles together. Sidecar tonal ramps are synthesized swatch metadata for the design panel, not additional website colors.

### Primary

- **Reference green — accent:** links, selected index text, input caret, keyboard focus and text selection. The dark counterpart uses a light green with the same role.

### Neutral

- **Warm paper — paper:** the page and search surface; dark appearance uses deep green paper.
- **Green ink — ink:** titles and ordinary text; dark appearance uses pale warm ink.
- **Quiet annotation — muted:** supporting metadata, summary prose, source details and marginal contents.
- **Selection wash — wash:** index hover and the current term.
- **Structural line — line:** navigation edges, section divisions, control borders and source separation.

**The Semantic Appearance Rule.** Switch all six roles together. Honor the system color preference until the reader chooses Light or Dark; store that choice per tab and site base path.

**The Adoption Evidence Rule.** Reserve yellow and green status fills for internal adoption. Green requires a documented consensus decision; external source rank never inherits adoption color. Switch the status ink/paper pairs with the appearance.

## Typography

**The Peripheral Legibility Rule.** Use 14px for the header and page directory, 15px for catalog terms, and at least 13px for search labels, subtitles, evidence annotations and metadata. Phone header controls may use 13px; keep its search input at 16px. Preserve the larger serif definition and title hierarchy instead of scaling the whole page.

**Display Font:** Newsreader, with Georgia and serif fallbacks.

**Body Font:** Manrope, with system-ui and sans-serif fallbacks.

Both variable fonts are self-hosted as TrueType files with OFL licenses, `font-display: swap` and available weights (200–800). The serif gives definitions room to be read; the sans-serif keeps navigation and evidence easy to scan.

### Hierarchy

- **Display:** homepage and term headings use the frontmatter display role. At widths up to 1150px they use (53px); at widths up to 767px they use (43px). Long headings wrap anywhere when necessary.
- **Definition:** core term meaning uses the definition role; mobile uses (25px, line-height 1.65). Full names use Newsreader (23px, weight 500, line-height 1.4), reducing to (19px) on mobile.
- **Term title:** curated summary links use the term-title role, reducing to (27px) on mobile. They follow Workflow, Harness, Model, LLM, Agent, Schema in both the index and the reading rows.
- **Headline:** section headings use the headline role. Definition comparison subheadings use Manrope (15px, line-height 1.5).
- **Body:** article text uses the body role, reducing to (14px) on mobile with the same line-height. Paragraphs and lists stay within (70ch). Homepage summaries use (14px, line-height 1.85), reducing to (13px), within rows capped at (75ch).
- **Navigation and labels:** index links use the navigation role at (15px), including mobile. Current links use weight (650). Labels and source metadata use (13px). The header and desktop page directory use (14px); mobile header controls use (13px). Mobile search input uses (16px).
- **Annotation and semantic labels:** source contexts, research notes, source records, revision records and the expandable page directory reuse the annotation size. Citations and relationship labels use the relation-label role; adoption tags use the stronger adoption-label role. These remain subordinate to definitions and their comparison headings.

**The Two Reading Speeds Rule.** Use the serif for term names and core meanings; use the sans-serif for retrieval, comparison labels, section labels, ordinary prose and evidence records.

## Layout

The header sits above a centered workspace capped at (1536px), containing the textual Plale Lab / Glossary identity, Index & search, PDF, Contribute on GitHub and the appearance action. Desktop uses an index (264px) and flexible main region. The index is sticky (20px from the viewport top), independently scrollable and capped at viewport height minus (40px). Reading is capped at (1150px), with padding (48px 48px 0).

The homepage introduction has a flexible text column and editorial note (192px), separated by (48px). The curated index presents Workflow, Harness, Model, LLM, Agent, Schema in that order, as open summary rows capped at (75ch) with structural top rules and padding (26px 0 6px). The first introduction paragraph remains above the index; later paragraphs and source/adoption policies follow it.

Term detail uses a flexible article and marginal record (174px), separated by (32px). Reading starts with title, optional full name and cited definition, then definition comparison, scope, includes, excludes and counterexamples, different usages and open boundaries, operational criteria, typed concept relationships, Lab working definition, sources and research gaps, and revision record. Includes and excludes are separate successive sections. The margin holds page contents, related terms and entry record.

At widths up to (1150px), the index narrows to (228px), reading padding becomes (38px 32px 0), and introduction and article become single columns. The marginal record follows the article; its page contents are replaced by a native expandable page directory between the definition and comparison section. The editorial note sits below the homepage introduction.

At widths up to (767px), the header wraps and the workspace becomes one column. Search stays visible above a native expandable catalog. Navigation gutters are (21px); reading padding becomes (29px 21px 0). Editorial and navigation notes are hidden. The curated rows retain their single-column order; related terms and entry record remain after the article. Section spacing reduces from (38px) to (32px).

The PDF build-record page shares header and reading typography in a standalone region capped at (1150px). Browser printing removes header, navigation, back link, marginal record and footer, flattens the grid and uses a monochrome surface. The separately generated PDF retains its existing document design and generation path.

**The Reading Space Rule.** Move supporting records after the article before compressing the text into a narrow three-column layout.

## Elevation & Depth

There are no shadows, gradients or lifted cards. Depth comes from paper, ink, tonal navigation states and structural dividers. Hover changes link decoration or applies wash; current navigation adds a line border. Keyboard focus uses an accent outline (3px) with offset (4px). No transition, animation, custom scrolling or motion token is authored.

**The Flat Reference Rule.** Use structural rules and tonal states to distinguish regions; retain the calm, flat reading surface.

## Shapes

Controls, navigation states and adoption tags have nearly square corners using the frontmatter control radius. Search, appearance control and selected index link have thin borders (1px). Summaries, comparison views and relationship rows remain unboxed, separated by thin rules. Strict subtype lists use a neutral vertical rule to expose nesting. The homepage reading notice retains the selected prototype's neutral left border (2px); this contextual treatment is not a general border-width scale.

## Components

**The Canonical Comparison Rule.** Keep Harness vs Workflow in a stable Harness section and link to it from Workflow. Cited comparison tables use neutral separators and independently attributed cells; on phones, each dimension becomes a stacked pair with visible term labels.

### Appearance action

The outlined button has transparent fill, ink text and a line border. Its minimum height is (36px) on desktop and (32px) on mobile. It names the available action: Dark in light appearance and Light in dark appearance, with an explicit accessible label. JavaScript reveals it and saves the choice in sessionStorage. Without JavaScript, CSS still follows system appearance.

### Search and result feedback

A visible label sits above an unboxed search input and Clear button inside the bordered search surface. The input has no native cancel icon; Clear resets it and returns keyboard focus. Input, buttons, links and catalog summary use the shared focus outline. Result count is a polite live status; empty results show a recovery message. No error or disabled variant is implemented.

Search uses case-insensitive, whitespace-separated tokens with AND matching. It covers titles, full names, aliases, definitions, scope, includes, excludes, ambiguities, operational criteria, adaptation and source titles. It filters index links and homepage summaries, includes definition comparisons and typed relationship conditions, and opens the catalog for a non-empty query. Query and appearance use sessionStorage scoped by the resolved index path, preserving them across static pages in the same tab. Storage failure is tolerated; queries never enter URLs or network requests.

### Persistent index and mobile catalog

Terms are ordinary static anchors. Current term uses `aria-current="page"`, wash, accent text, a line border and stronger weight. Hover applies wash without underline. Desktop items have minimum height (44px); mobile items have minimum height (46px). Full names form a smaller muted second line. The homepage has no current term.

Mobile uses native `details` and `summary`. JavaScript initially closes the catalog on mobile with an empty query, opens it on desktop or for a query, and synchronizes at the breakpoint. Readers can expand it manually. Clearing search does not forcibly close an expanded catalog. Without JavaScript, the generated open catalog and static links remain available, with a note explaining that search requires JavaScript.

### Curated term summaries

The reading order is Workflow, Harness, Model, LLM, Agent, Schema. Open serif-linked term rows have thin separators, scope subtitles and cited summaries. Definition comparisons use neutral labeled rows. Colored tags are reserved for the internal Lab adoption status.

### Definition comparisons and typed relationships

Comparison views begin with a thin top rule and padding (18px 0 5px). Each has a sans-serif source label, muted context and cited prose. Relationship rows use the same flat vocabulary with padding (16px 0 1px), a stronger relation statement and a muted type label. Conditions and citations follow the relationship. Only strict is-a subtypes use nested lists and a neutral vertical rule; uses and supports/orchestrates stay as labeled rows.

**The Strict Nesting Rule.** Nest only a documented is-a relationship. Keep composition and control relationships visibly typed, with their conditions and evidence beside them.

### Adoption tags and page directory

Adoption tags use compact padding (4px 8px), the control radius and the adoption-label role. Proposed / not ratified is yellow; adopted by consensus is green only when a decision is recorded. Tags supplement explicit status text. Source tier metadata stays muted. The page directory uses native details and summary with a minimum summary height (36px), thin horizontal rules and fragment links; it appears at the record-after-article breakpoint and retains shared keyboard focus.

### Article, sources and marginal record

Definitions have the largest reading text after the title. Source links wrap long addresses, followed by author/kind and version/locator/access details in smaller muted text. Marginal contents use native fragment links; below 1150px a native expandable page directory takes their place. Compact is-a lists show strict subtypes; uses and supports/orchestrates remain labeled relation rows with cited conditions. Related terms are static links and never filtered by search. Entry version, update, status and adoption decision remain separate from source authority.

### Keyboard and static fallback

A skip link precedes the header, becomes visible on focus and targets main. Native controls retain visible focus. Homepage, term, policy and related links work without JavaScript. The shared handbook source supplies content; this design retains six active terms, source records, TeX, bibliography and PDF workflow. Local HTML previews link the checksum-verified historical PDF with its actual edition; publication follows the existing CI workflow.

## Do's and Don'ts

### Do:

- **Do** preserve the approved persistent navigation and editorial reading pairing.
- **Do** use all six semantic color roles together in light and dark appearance.
- **Do** keep search visible on mobile and related links outside search filtering.
- **Do** preserve native anchors, catalog disclosure, keyboard focus and static fallbacks.
- **Do** retain glossary prose, versioned sources and the distinction between proposal and adoption.
- **Do** keep comparison views, source tiers and editorial interpretations neutral, reserving adoption fills for explicit internal status.
- **Do** use strict subtype nesting only for is-a and retain cited conditions for uses and supports/orchestrates.

### Don't:

- **Don't** replace the self-hosted reading fonts with a system display face.
- **Don't** convert open definition rows into lifted cards or add decorative shadows.
- **Don't** compress the desktop marginal column into the mobile article.
- **Don't** put the query in URLs or send search input to a server.
- **Don't** introduce decorative eyebrows above the homepage, term title or build-record title.
- **Don't** show green adoption status without a recorded consensus decision.
