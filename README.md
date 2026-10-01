# The Victory Royale Report (website)

Static site for the weekly newsletter. Hosted free on GitHub Pages.

## Add a new issue (the Tuesday task does this automatically)
1. Make `issues/<slug>/` (e.g. `2026-week-04`) with `issue.html` (the newsletter body markup) and the PDF.
2. Add an entry to the top of `issues.json` (slug, title, date, date_label, pdf, headline, description).
3. Run `python3 build_site.py`, then commit and push. GitHub Pages redeploys in about a minute.

## Files
- `newsletter.css` – the newsletter's own styles (shared with the PDF)
- `build_site.py` – builds index.html (latest issue), issues/*/index.html, archive/, sitemap.xml, robots.txt, site.css
- `site.json` – site URL and name. Update `site_url` once the GitHub Pages URL is known.
