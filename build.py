#!/usr/bin/env python3
"""Génère le site statique dans docs/ à partir des articles Markdown de articles/.

Chaque article commence par un en-tête :
---
title: Titre
description: Résumé en une phrase (affiché sur Google)
date: 2026-11-04
category: Aides
---
"""
import html, json, re, shutil
from datetime import date
from pathlib import Path
import markdown

RACINE = Path(__file__).parent
SORTIE = RACINE / "docs"
BASE = "https://ingaaal.github.io/site-auto"
NOM = "Fin de Mois"
MOIS = ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"]

def date_fr(d):
    y, m, j = map(int, d.split("-"))
    return f"{j} {MOIS[m-1]} {y}"

def lire(p):
    txt = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", txt, re.S)
    meta = dict(l.split(": ", 1) for l in m.group(1).splitlines() if ": " in l)
    meta["slug"] = p.stem
    meta["corps"] = markdown.markdown(m.group(2), extensions=["tables"])
    return meta

def page(titre, desc, url, contenu, schema=None):
    sch = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>' if schema else ""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titre)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta name="google-site-verification" content="ZIUyGgv791zJBAkmzFOC50TGnV4PW-4g3ofcVsOqbW4" />
<meta property="og:title" content="{html.escape(titre)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="{BASE}/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700;800&family=Literata:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{BASE}/style.css">
{sch}
</head>
<body>
<header class="tete"><div class="w">
<a class="logo" href="{BASE}/" aria-label="Fin de Mois, accueil"><svg class="logo-mark" viewBox="0 0 48 48" aria-hidden="true"><g transform="rotate(-6 24 24)"><rect x="7" y="9" width="34" height="33" rx="4" fill="#fff" stroke="currentColor" stroke-width="2.6"/><path d="M7 13a4 4 0 0 1 4-4h26a4 4 0 0 1 4 4v5H7z" fill="currentColor"/><rect x="15" y="5" width="3.2" height="8" rx="1.6" fill="currentColor"/><rect x="29.8" y="5" width="3.2" height="8" rx="1.6" fill="currentColor"/><text x="24" y="36.5" text-anchor="middle" font-family="Bricolage Grotesque,system-ui,sans-serif" font-weight="800" font-size="16" fill="currentColor" letter-spacing="-.5">31</text></g><path class="logo-cercle" d="M12.5 29.5c1-6.8 9.6-9.6 16.6-8.4 7.3 1.3 10.4 6.6 8.6 11.4-1.9 5-9.7 7.4-16.4 6.3C14.6 37.7 11.2 33.9 12.8 28.6c.9-3 3.4-4.9 6-6" fill="none" stroke="#d1243b" stroke-width="2.2" stroke-linecap="round"/></svg><span class="logo-txt"><span class="logo-nom">Fin de <span class="logo-mois">Mois</span></span><span class="logo-sous">le budget étudiant</span></span></a>
<nav><a href="{BASE}/#articles">Articles</a><a href="{BASE}/a-propos/">À propos</a></nav>
</div></header>
{contenu}
<footer><div class="w"><span>Fin de Mois, le budget étudiant expliqué simplement.</span><span>Infos vérifiées sur les sources officielles.</span></div></footer>
</body>
</html>"""

def construire():
    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    SORTIE.mkdir()
    shutil.copy(RACINE / "static" / "style.css", SORTIE / "style.css")
    shutil.copy(RACINE / "static" / "favicon.svg", SORTIE / "favicon.svg")
    (SORTIE / ".nojekyll").write_text("")

    arts = sorted((lire(p) for p in (RACINE / "articles").glob("*.md")), key=lambda a: a["date"], reverse=True)

    for a in arts:
        url = f"{BASE}/{a['slug']}/"
        autres = sorted([b for b in arts if b["slug"] != a["slug"]], key=lambda b: b["category"] != a["category"])[:3]
        aussi = ('<aside class="aussi"><h2>À lire aussi</h2><ul>' + "".join(f'<li><a href="{BASE}/{b["slug"]}/">{html.escape(b["title"])}</a></li>' for b in autres) + '</ul></aside>') if autres else ""
        maj = f'<p class="maj">Mis à jour le {date_fr(a["updated"])}</p>' if a.get("updated") else ""
        contenu = f"""<main class="article">
<span class="cat">{html.escape(a['category'])}</span>
<h1>{html.escape(a['title'])}</h1>
<p class="meta">Publié le {date_fr(a['date'])}</p>
<div class="corps">{a['corps']}</div>
{maj}
{aussi}
<p style="margin-top:40px"><a href="{BASE}/">← Tous les articles</a></p>
</main>"""
        schema = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"],
                  "description": a["description"], "datePublished": a["date"],
                  "dateModified": a.get("updated", a["date"]), "inLanguage": "fr"}
        d = SORTIE / a["slug"]; d.mkdir()
        (d / "index.html").write_text(page(f"{a['title']} | {NOM}", a["description"], url, contenu, schema), encoding="utf-8")

    items = "".join(f"""<a class="art" href="{BASE}/{a['slug']}/"><time datetime="{a['date']}">{date_fr(a['date'])}</time>
<div><span class="cat">{html.escape(a['category'])}</span><h3>{html.escape(a['title'])}</h3><p>{html.escape(a['description'])}</p></div></a>""" for a in arts)
    accueil = f"""<main class="w">
<section class="une">
<div><h1>Le budget étudiant, sans prise de tête.</h1>
<p>Aides, bons plans, démarches : ce que tu peux vraiment toucher ou économiser, avec les montants à jour et les sources officielles.</p></div>
<div class="ticket" aria-hidden="true"><b>Exemple de mois étudiant</b>
<div><span>20 repas Crous</span><span>20,00 €</span></div>
<div><span>Loyer studio</span><span>450,00 €</span></div>
<div><span>APL</span><span>− 180,00 €</span></div>
<div><span>Bourse échelon 2</span><span>− 307,10 €</span></div>
<div class="tot"><span>Il te reste</span><span>17,10 €</span></div></div>
</section>
<section class="liste" id="articles"><h2>Derniers articles</h2>{items}</section>
</main>"""
    (SORTIE / "index.html").write_text(page(f"{NOM} : le budget étudiant expliqué simplement", "Aides étudiantes, bourses, APL, bons plans : les montants à jour et les démarches expliquées simplement.", f"{BASE}/", accueil), encoding="utf-8")

    apropos = f"""<main class="article"><h1>À propos</h1><div class="corps">
<p>Fin de Mois explique simplement les aides, les démarches et les bons plans qui comptent quand on est étudiant.</p>
<p>Chaque article est vérifié à partir des sources officielles (service-public.fr, caf.fr, lescrous.fr, etudiant.gouv.fr) et mis à jour quand les règles changent. Les montants peuvent évoluer : en cas de doute, la source officielle fait toujours foi.</p>
</div></main>"""
    (SORTIE / "a-propos").mkdir()
    (SORTIE / "a-propos" / "index.html").write_text(page(f"À propos | {NOM}", "Qui écrit Fin de Mois et comment les articles sont vérifiés.", f"{BASE}/a-propos/", apropos), encoding="utf-8")

    urls = [f"{BASE}/", f"{BASE}/a-propos/"] + [f"{BASE}/{a['slug']}/" for a in arts]
    lastmod = {f"{BASE}/{a['slug']}/": a.get("updated", a["date"]) for a in arts}
    sm = "".join(f"<url><loc>{u}</loc><lastmod>{lastmod.get(u, date.today().isoformat())}</lastmod></url>" for u in urls)
    (SORTIE / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    (SORTIE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    print(f"{len(arts)} articles générés dans docs/")

if __name__ == "__main__":
    construire()
