#!/usr/bin/env python3
"""Builds the Victory Royale Report website from issues.json.

Each issue lives in issues/<slug>/ with:
  issue.html  - the newsletter body markup (same markup used for the PDF)
  <pdf name>  - the one-page PDF
Run:  python3 build_site.py
Outputs: index.html (latest issue), issues/<slug>/index.html, archive/index.html,
sitemap.xml, robots.txt
"""
import json, os, html, re

ROOT = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(ROOT, "site.json")))
issues = json.load(open(os.path.join(ROOT, "issues.json")))
issues.sort(key=lambda i: i["date"], reverse=True)
SITE = cfg["site_url"].rstrip("/")
NAME = cfg["site_name"]

# ---------- CSS: print newsletter CSS scoped to .sheet + web layer ----------
css = open(os.path.join(ROOT, "newsletter.css")).read()
css = re.sub(r"@page\s*\{[^}]*\}", "", css)
css = css.replace("html,body { background:var(--paper); }", "")
css = re.sub(r"(^|\n)body \{", r"\1.sheet {", css)

WEB_CSS = """
body.site { margin:0; background:var(--deck); color:var(--ink); font-family:'Inter',system-ui,sans-serif; }
:root { --deck:#dcd5c6; }
.bar { background:var(--ink); color:#fff; font-family:'Inter',sans-serif; }
.bar-in { max-width:1120px; margin:0 auto; padding:10px 16px; display:flex; gap:18px; align-items:center; flex-wrap:wrap; }
.bar .brand { font-family:'Inter',sans-serif; font-weight:900; letter-spacing:.3px; text-transform:uppercase; font-size:15px; color:#fff; text-decoration:none; margin-right:auto; }
.bar .brand span { color:#ff4d5e; }
.bar a.nav { color:#fff; text-decoration:none; font-size:14px; font-weight:600; opacity:.85; }
.bar a.nav:hover, .bar a.nav:focus-visible { opacity:1; text-decoration:underline; }
.bar a.pdf { background:var(--red); color:#fff; padding:6px 12px; border-radius:3px; font-weight:700; font-size:13px; text-decoration:none; }
.wrap { padding:28px 16px 40px; }
.sheet { width:8.5in; max-width:100%; margin:0 auto; box-shadow:0 1px 2px rgba(0,0,0,.15),0 12px 40px rgba(0,0,0,.18); background:var(--paper); }
@media (min-width:1180px) { .wrap { zoom:1.3; } }
.issue-meta { max-width:8.5in; margin:0 auto 14px; display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; font-size:14px; color:#3d3a33; }
.issue-meta a { color:var(--red); font-weight:700; }
@media (max-width:860px) {
  .wrap { padding:12px 0 32px; }
  .bar .brand { font-size:13px; }
  .bar-in { gap:12px; }
  .issue-meta { padding:0 16px; }
  .sheet { width:auto; box-shadow:none; padding:16px !important; font-size:15px; line-height:1.45; }
  .mast { flex-direction:column; align-items:flex-start; gap:6px; }
  .mast h1 { font-size:34px; white-space:normal; line-height:.95; }
  .mast .meta { text-align:left; white-space:normal; font-size:13px; }
  .mast .meta .iss { font-size:15px; }
  .sub { flex-direction:column; gap:2px; font-size:14px; }
  .ticker { font-size:12.5px; }
  .grid { grid-template-columns:1fr; }
  h2 { font-size:21px; margin-top:10px; }
  h2 small { font-size:11px; }
  h3 { font-size:14px; }
  .score, .trade .deal, .pr .tm { font-size:15px; }
  .award { grid-template-columns:96px 1fr; }
  .award .t { font-size:12px; }
  .pr .rk { font-size:22px; width:32px; }
  .pr .rec { font-size:12px; }
  .verdict { font-size:11px; }
  table.luck { font-size:13px; }
  table.luck th { font-size:10.5px; }
  .note { font-size:12px; }
}
.archive { max-width:760px; margin:0 auto; background:var(--paper); padding:28px 24px; box-shadow:0 12px 40px rgba(0,0,0,.18); }
.archive h1 { font-family:'Inter',sans-serif; font-weight:900; text-transform:uppercase; font-size:30px; letter-spacing:-.5px; margin:0 0 4px; }
.archive p.lede { margin:0 0 18px; color:#3d3a33; font-family:'Lora',serif; font-style:italic; }
.archive ol { list-style:none; margin:0; padding:0; border-top:2.5px solid var(--ink); }
.archive li { padding:12px 0; border-bottom:1px dotted #999; display:grid; grid-template-columns:1fr auto; gap:4px 12px; }
.archive li a.t { font-weight:800; font-size:17px; color:var(--ink); text-decoration:none; }
.archive li a.t:hover { color:var(--red); }
.archive li .d { color:#5b5b5b; font-size:13px; }
.archive li .h { grid-column:1 / -1; font-size:14px; }
.archive li a.p { font-size:13px; color:var(--red); font-weight:700; }
footer.site { text-align:center; font-size:12px; color:#4a463e; padding:0 16px 30px; }
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=Lora:ital@1&display=swap" rel="stylesheet">')
FONT_FIX = "@font-face{font-family:'Inter Display';src:local('Inter Display'),local('Inter');}\n"

def page(title, desc, canonical, rel, body, og_type="article"):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="{og_type}"><meta property="og:url" content="{canonical}"><meta property="og:site_name" content="{html.escape(NAME)}">
<meta name="twitter:card" content="summary">
{FONTS}
<link rel="stylesheet" href="{rel}site.css">
</head><body class="site">
<header class="bar"><div class="bar-in"><a class="brand" href="{rel}">The Victory <span>Royale</span> Report</a>
<a class="nav" href="{rel}">Latest</a><a class="nav" href="{rel}archive/">Archive</a></div></header>
{body}
<footer class="site">{html.escape(NAME)} · a {html.escape(cfg['league_blurb'])} · Scores from ESPN. Roasts from the Commish.</footer>
</body></html>"""

def issue_body(iss, rel, issue_dir_rel):
    inner = open(os.path.join(ROOT, "issues", iss["slug"], "issue.html")).read()
    pdf = f'{issue_dir_rel}{iss["pdf"]}'
    return (f'<main class="wrap"><div class="issue-meta"><span>{html.escape(iss["title"])} · {iss["date_label"]}</span>'
            f'<span><a href="{pdf}">Download the PDF</a></span></div>'
            f'<article class="sheet">{inner}</article></main>')

open(os.path.join(ROOT, "site.css"), "w").write(FONT_FIX + css + WEB_CSS)

urls = []
for iss in issues:
    d = os.path.join(ROOT, "issues", iss["slug"])
    canon = f"{SITE}/issues/{iss['slug']}/"
    t = f"{iss['title']} | {NAME}"
    open(os.path.join(d, "index.html"), "w").write(page(t, iss["description"], canon, "../../", issue_body(iss, "../../", "")))
    urls.append((canon, iss["date"]))

latest = issues[0]
open(os.path.join(ROOT, "index.html"), "w").write(page(
    f"{NAME}: {latest['title']}", latest["description"], f"{SITE}/", "",
    issue_body(latest, "", f"issues/{latest['slug']}/"), og_type="website"))
urls.insert(0, (f"{SITE}/", latest["date"]))

items = "".join(
    f'<li><a class="t" href="../issues/{i["slug"]}/">{html.escape(i["title"])}</a><span class="d">{i["date_label"]}</span>'
    f'<span class="h">{html.escape(i["headline"])}</span><a class="p" href="../issues/{i["slug"]}/{i["pdf"]}">PDF</a></li>'
    for i in issues)
os.makedirs(os.path.join(ROOT, "archive"), exist_ok=True)
open(os.path.join(ROOT, "archive", "index.html"), "w").write(page(
    f"Archive | {NAME}", f"Every issue of {NAME}, the weekly newsletter of the {cfg['league_blurb']}.",
    f"{SITE}/archive/", "../",
    f'<main class="wrap"><section class="archive"><h1>Archive</h1><p class="lede">Every issue, newest first.</p><ol>{items}</ol></section></main>',
    og_type="website"))
urls.append((f"{SITE}/archive/", latest["date"]))

open(os.path.join(ROOT, "sitemap.xml"), "w").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")
open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
print("built", len(issues), "issue(s)")
