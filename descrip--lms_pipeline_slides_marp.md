https://pretalx.com/wtd-australia-2026/talk/review/U7C8TWZTM8BLVSJCAVPWWXH3K7XPADXT


# The LMS as a Build Target: Shifting the Source of Truth to a Publishing Pipeline 

A learning management system is a good place to deliver a course but often a poor place to author one. This talk presents a lightweight, static-site-generator-inspired workflow that produces LMS-ready HTML pages, PDF assessment briefs, and Common Cartridge packages from a plain-text repository of Markdown and other source files. Drawing on its use across several university offerings, I'll discuss it's conception, motivations, and planning. Leading from that, what worked, what broke, and how treating the LMS as a deployment target improved version control, metadata management, citations, maintenance, and reuse. More importantly, the approach returned ownership to domain experts, reduced update times from weeks to minutes, and enabled AI-assisted review of structured course content.


## Talk Outline

This is an outline for the presentation, open to adjustments if you wish.

- **The problem.** Authoring directly in an LMS makes it the de facto source of truth, with inevitable content drift, limited version history, and potential format and platform lock-in.

- **The reframing.** We framed these as a requirements list, prioritising: learning materials' currency, ownership, meaningful version history, single-sourced metadata, multi-format publishing, citation management, portability, and accessibility.

- **The mental model.** Static-site-generator thinking applied to an LMS -- the same inversion many documentarians use for docs portals: the repository is canonical, a build process renders the required outputs, and the LMS becomes a deployment target.

- **The pipeline, end to end.** YAML, Markdown, and BibTeX transformed through a build process that produces HTML module pages, PDF assessment briefs, teaching notes, and a Common Cartridge package for bulk import into Canvas.

- **Patterns and (limited) demonstrations.** Examples include template tags for single-sourced metadata, multi-format output, wiki-style links, and a diff tool that compares a local build with a live Canvas export to answer: "What actually changed on the platform?" Importantly, the focus here is very much high-level architecture and author experience.

- **The payoff.** Ownership returned to domain experts, updates to rapidly changing content dropped from weeks to minutes, and structured (local) source material enabled AI-assisted review.

- **What broke.** Canvas import quirks included unexpected overwrite behaviour and duplicated assets. Other limitations included weak Microsoft Word support and a manual "final 5 percent" of work after each import. Complications accommodating the university compliance process.


### Speaker Bio

I'm a lecturer in UX, web, and interaction design at Torrens University Australia. I spend a lot of time authoring course materials. My background bridges design and software: I began in graphic and interactive design before moving into programming and education. In the Python community, I'm best known as the author of *[Learn Python Visually: Creative Coding with Processing.py](https://nostarch.com/learn-python-visually)* (No Starch Press, 2021), which introduces non-programmers to Python through visual, graphics-based creative coding. I've also contributed substantially to the official documentation of open-source projects, including `p5.js` and the Python library `py5`, and have presented at SIGGRAPH, PyCon, and Processing Foundation events.


##

I'm available to present either in person in Melbourne or as part of a prerecorded session with live Q&A.

