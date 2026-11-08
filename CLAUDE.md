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
