# The LMS as a Build Target

*Slides for a [Write the Docs](https://www.writethedocs.org/conf/australia/2026/) talk on moving course content from the LMS to a plain-text build pipeline using [Torrenzo](https://github.com/tabreturn/torrenzo).*

---

This presentation is a [Marp](https://marp.app) slide deck. You can view the pre-rendered PDF below or render the deck locally for features such as animated bullet points and presenter notes.


## PDF Version

[deck.pdf](deck.pdf)


## Rendering

**Note:** `style_marp/` is normally a symlink to the shared [marp-style](https://github.com/tabreturn/marp-style) theme repo. If the link is broken on your machine, overwrite it with a real copy -- `rm style_marp && git clone https://github.com/tabreturn/marp-style style_marp` -- then install Marp once with `cd style_marp && npm install`.

Live preview (watch + presenter view):

```bash
./render
```

Export PDF:

```bash
./render --pdf
```

The deck source is `slides/deck.md`; talk notes live in `outline.md`.

