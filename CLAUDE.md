# Ourty — wellness blog

Static site built with `build.py` (Python 3 stdlib only), hosted on GitHub Pages from `docs/` on `main`.
Live URL: https://ourtyy.github.io/Ourty/ — repo: github.com/Ourtyy/Ourty (push via SSH).
The owner speaks Spanish: always reply in Spanish. Articles are written in English.

## Workflow
- New articles go to `content/drafts/<slug>.md`. The owner reviews every article before it goes live.
- Preview: `python3 build.py preview` (output in `preview/`, served by the `ourty-site` launch config on port 8766).
- Publish only when the owner says so: `python3 build.py publish <slug>`, then `git add -A && git commit -m "Publish <slug>" && git push`.
- Never put AdSense IDs or other config in unless the owner gives them.

## Article format
```
---
title: Clear, specific title (55–65 chars ideal)
description: One-sentence summary for Google (140–160 chars)
category: nutrition | fitness | mind | sleep | habits | recipes
---
Intro paragraph (hook, no heading)...

## Section headings (## and ###)
- lists, **bold**, *italic*, [links](https://...), > tip blockquotes

## The bottom line
## Sources
- Organisation — [Page title](https://real-url)
```

## Writing rules
- 900–1,400 words, plain friendly English, short paragraphs, practical takeaways.
- Original angle: never copy or closely paraphrase another site. Synthesize from several sources.
- Every health claim must come from a trustworthy source (WHO, NHS, CDC, NIH, Mayo Clinic, Harvard Health, peer-reviewed studies, major news coverage of studies). Open each source to confirm it says what you claim; only cite URLs you have actually loaded.
- Trends: explain what's new, what the evidence actually says, and be honest when evidence is weak or hype. No miracle cures, no diagnosing, no supplement/drug dosing advice; say "talk to a doctor" where relevant.
- Avoid topics already covered (check `content/posts` and `content/drafts`).

## Photos (every article needs one; recipes 2–3)
- `python3 find_image.py search "<english keywords>"` → up to 8 Unsplash candidates in `.image-candidates/1.jpg…8.jpg` (needs `unsplash_key.txt`, which is git-ignored — never print, move or commit it).
- LOOK at each candidate (Read the jpg files) and choose a beautiful, bright, warm, "Pinterest-style" photo that matches the article: natural light, soft tones, appetising food, calm lifestyle scenes. Avoid dark, cluttered, branded, or clinical images, and faces in distress.
- Main photo: `python3 find_image.py attach <N> <article-slug> "<alt text describing the photo>"`.
- Extra photos inside the body (recipes: after the ingredients/method and near the variations): `python3 find_image.py pick <N> <name>` prints a ready `![alt](url) Photo by …` line — paste it on its own line between paragraphs, replacing `<alt text>`. Run a new search before each pick if you need a different subject.
- Keep the credit line exactly as printed (Unsplash requires crediting the photographer).
