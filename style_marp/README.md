# Marp Notes


## Setup

```bash
cd c.tech-subject-dev/style_marp
npm install @marp-team/marp-cli
```


## Run (live preview)

```bash
cd c.tech-subject-dev/style_marp
cat marp-base.css marp-fonts.css > /tmp/marp.css && npx marp -w -p --html --theme /tmp/marp.css <slides>.md
```


## Export to PDF

```bash
cat marp-base.css marp-fonts.css > /tmp/marp.css && npx marp --pdf --html --allow-local-files --theme /tmp/marp.css <slides>.md
```


## Files

- `marp-base.css` -- theme rules (edit this for styling)
- `marp-fonts.css` -- `@font-face` blocks with base64-embedded fonts (edit this for fonts)
- `<slides>.md` -- slide source (edit this for content)


## Images

Slide-decks reference images (including the title splash background) with relative paths. Each deck's source folder must contain any images it uses; copy all required assets (including [title_bg.png](title_bg.png)) into each deck's source folder.


## Fonts

Fonts are base64-embedded in `marp-fonts.css`. This is beacuse Marp won't load font files (unless you provide an absoulte URL to Google Fonts or similar). To replace a font:

1. Place the `.woff2` file in the project directory
2. Encode it: `base64 -w0 font.woff2`
3. Replace the `src: url(...)` value in `marp-fonts.css` with `url(data:font/woff2;base64,<base64-here>)`

