# AGENTS.md

Marp slide-deck repository for the Write the Docs Australia 2026 talk "The LMS as a Build Target" (Torrens University). Content-only repo: Markdown slide sources, a Marp theme, and images. No application code.

## Repository layout

- `style_marp/` — reusable Marp theme toolkit (kept self-contained; see its `README.md`)
  - `marp-base.css` — theme rules (Marp theme `TorrensUni`, extends Gaia). Edit for styling.
  - `marp-fonts.css` — `@font-face` blocks with **base64-embedded fonts** (Marp cannot load font files). To swap a font: `base64 -w0 font.woff2`, then replace the `src: url(...)` with `url(data:font/woff2;base64,<...>)`.
  - `package.json` — only dependency: `@marp-team/marp-cli`
  - `template.md` — starter deck showing slide conventions
  - `title_bg.png` — title splash background
- `marp--<deck_name>/` — one directory per deck (e.g. `marp--lms_pipeline_slides/`), containing `deck.md` plus **all images it references** (each deck copies its own assets, including `title_bg.png`)
- `descrip--<deck_name>_marp.md` — talk abstract / proposal text for that deck
- `render/` — output directory for rendered files (gitignored along with `marp--*/*.html` and `marp--*/*.pdf`)

## Commands

The theme CSS is split into two files that must be concatenated before use — Marp is always invoked with the combined file:

```bash
cd style_marp
npm install                                # first time; installs marp-cli

# Live preview (watch + server)
cat marp-base.css marp-fonts.css > /tmp/marp.css && npx marp -w -p --html --theme /tmp/marp.css <deck>.md

# Export PDF (from within a deck's directory, or point at its deck.md)
cat marp-base.css marp-fonts.css > /tmp/marp.css && npx marp --pdf --html --allow-local-files --theme /tmp/marp.css <deck>.md
```

Note: `--allow-local-files` is required for PDF export because decks reference images via relative paths.

## Deck conventions

Reference examples: `style_marp/template.md` (skeleton) and the sibling repo `../cc-fest-noc-py5/marp_slides/deck.md` (full worked deck using the same theme — the canonical formatting reference).

### Structure

- Front matter: `marp: true`, `theme: TorrensUni`, `notes: ...`
- Per-slide directives (paginate, background/color) go in HTML comments *after* the slide content; `_`-prefixed for single-slide scope
- Speaker notes are a second HTML comment below the directives, as `- ` bullet lists; cue upcoming slides with `... [NEXT SLIDE]`
- Title slide: `# ***Deck Title***` with `_backgroundImage: "url(title_bg.png)"`, `_backgroundSize: "cover"`, `_color: var(--color-background)`
- Section-divider slides: a lone `# Section Name` that sets `backgroundColor` (e.g. `darkslategrey`, `maroon`, `indigo` — one color per section) plus `color: var(--color-background)`; the first divider also sets `paginate: true`
- Content slides: `## Section » Subtopic` headings

### Bullets

- Sentence case; key terms bolded with `**...**`
- Labeled bullets use theme tags: `* <highlight>Label:</highlight> description`, with two-trailing-space line breaks for continuation lines; `<smaller>...</smaller>` for secondary lines (both defined in `marp-base.css`)
- Progressive reveal: duplicate the slide and append one item per copy

### Image slides

Full-bleed images get their own slide with no heading:

```markdown
<!--
_backgroundColor: black
_paginate: false
-->
![bg 50%](setup--02-thonny-install.png)
> https://source-url-or-caption
```

- `_backgroundColor`: `black` for screenshots, `white`/`#EEE` for diagrams and light images
- Always `_paginate: false` on image slides
- Sizing via Marp bg filters: `![bg contain]`, `![bg 50%]`, `![bg 70%]`, `![bg 120%]` depending on how much bleed is wanted
- Optional caption/source as a blockquote (`> ...`) after the image

### Misc

- Divider between side-by-side code comparisons: `<hr style="color:rgba(255,255,255,0.3)" />`
- Centered quote/interstitial slides: `_class: lead` with italic text
- Image files named `<section>--<NN>-<description>.png` (double-hyphen, numbered for sequences)

## Gotchas

- Deck directories and description files use a `name--topic` double-hyphen naming scheme (`marp--lms_pipeline_slides`, `descrip--..._marp.md`); follow it for new decks.
- Never edit `marp-fonts.css` casually — it contains huge base64 font blobs; a bad edit breaks the whole theme.
- Slide-deck images use relative paths; any image added to a deck must be copied into that deck's folder, not referenced from elsewhere.
