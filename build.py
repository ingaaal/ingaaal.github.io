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
import html, json, re, shutil, sys, unicodedata
from datetime import date
from pathlib import Path
import markdown

RACINE = Path(__file__).parent
SORTIE = RACINE / "docs"
BASE = "https://ingaaal.github.io/site-auto"
NOM = "Fin de Mois"
CATEGORIES = ["Aides", "Logement", "Bons plans", "Banque", "Jobs", "Démarches"]
MOIS = ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"]

def date_fr(d):
    y, m, j = map(int, d.split("-"))
    return f"{j} {MOIS[m-1]} {y}"

def lire(p):
    txt = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", txt, re.S)
    meta = dict(l.split(": ", 1) for l in m.group(1).splitlines() if ": " in l)
    meta["slug"] = p.stem
    meta["md"] = m.group(2)
    meta["corps"] = liens_sources(markdown.markdown(m.group(2), extensions=["tables"]))
    return meta

def slugifier(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")

def url_cat(c):
    return f"{BASE}/categorie/{slugifier(c)}/"

def texte_brut(md):
    """Markdown d'une ligne -> texte simple (pour les données structurées)."""
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", md)
    t = re.sub(r"[*_`]", "", t)
    return " ".join(t.split())

def faq(corps_md):
    """Extrait les paires question/réponse de la section « Questions fréquentes »."""
    m = re.search(r"^## Questions fréquentes\s*$(.*?)(?=^## |^<div class=\"sources\"|\Z)", corps_md, re.M | re.S)
    if not m:
        return []
    paires, q, rep = [], None, []
    for bloc in re.split(r"\n\s*\n", m.group(1).strip()):
        bloc = bloc.strip()
        b = re.fullmatch(r"\*\*(.+?)\*\*", bloc)
        if b:
            if q and rep:
                paires.append((q, " ".join(rep)))
            q, rep = texte_brut(b.group(1)), []
        elif q and bloc:
            rep.append(texte_brut(bloc))
    if q and rep:
        paires.append((q, " ".join(rep)))
    return paires

def liens_sources(h):
    """Rend cliquables les liens Markdown [texte](https://...) du bloc sources (HTML brut)."""
    def rempl(m):
        bloc = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                      lambda l: f'<a href="{html.escape(l.group(2))}" rel="noopener">{l.group(1)}</a>', m.group(0))
        return bloc
    return re.sub(r'<div class="sources">.*?</div>', rempl, h, flags=re.S)

def verifier(arts):
    """Contrôle les articles avant publication. Erreurs = build refusé ; alertes = à corriger si possible."""
    erreurs, alertes = [], []
    slugs = {a["slug"] for a in arts}
    pages = slugs | {"a-propos"} | {f"categorie/{slugifier(c)}" for c in CATEGORIES}
    titres = {}
    for a in arts:
        n = f"articles/{a['slug']}.md"
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", a["slug"]):
            erreurs.append(f"{n} : slug invalide (minuscules, chiffres et tirets uniquement)")
        for champ in ("title", "description", "date", "category"):
            if not a.get(champ, "").strip():
                erreurs.append(f"{n} : champ « {champ} » manquant dans l'en-tête")
        for champ in ("date", "updated"):
            if a.get(champ):
                try:
                    date.fromisoformat(a[champ])
                except ValueError:
                    erreurs.append(f"{n} : {champ} invalide « {a[champ]} » (format AAAA-MM-JJ)")
        if a.get("category") and a["category"] not in CATEGORIES:
            erreurs.append(f"{n} : catégorie « {a['category']} » inconnue ({', '.join(CATEGORIES)})")
        lg = len(a.get("description", ""))
        if not 140 <= lg <= 160:
            erreurs.append(f"{n} : description de {lg} caractères (il en faut 140 à 160)")
        if a.get("title") in titres:
            erreurs.append(f"{n} : même titre que articles/{titres[a['title']]}.md")
        titres[a.get("title")] = a["slug"]
        md = a["md"]
        if "## Questions fréquentes" not in md:
            erreurs.append(f"{n} : section « ## Questions fréquentes » absente")
        elif len(faq(md)) < 3:
            erreurs.append(f"{n} : moins de 3 questions lisibles dans la FAQ (question seule en **gras**, ligne vide, réponse)")
        if not re.search(r'<div class="sources"><h2>Sources</h2>.+?</div>', md, re.S):
            erreurs.append(f"{n} : bloc sources absent ou mal formé")
        if not any("erreur" in h.lower() for h in re.findall(r"^## (.*)", md, re.M)):
            erreurs.append(f"{n} : pas de section « erreurs » (## Les erreurs qui coûtent cher)")
        for cible in re.findall(r"\]\(/site-auto/([^)#?]*)", md):
            if cible.strip("/") not in pages:
                erreurs.append(f"{n} : lien interne cassé vers /site-auto/{cible}")
        for cible in re.findall(r"\]\(([^)]*)\)", md):
            if not cible.startswith(("/site-auto/", "https://", "http://", "#", "mailto:")):
                erreurs.append(f"{n} : lien « {cible} » au mauvais format (attendu /site-auto/<slug>/ ou https://...)")
        nb_liens = len(set(re.findall(r"\]\(/site-auto/([^)#?]*)", md)))
        if nb_liens < 2:
            alertes.append(f"{n} : {nb_liens} lien(s) interne(s), 2 recommandés")
        mots = len(re.sub(r'<div class="sources">.*', "", md, flags=re.S).split())
        if not 700 <= mots <= 1200:
            alertes.append(f"{n} : {mots} mots (700 à 1 200 recommandés)")
    return erreurs, alertes

def image_partage(a, dossier):
    """Image 1200x630 pour les partages (WhatsApp, réseaux). Mise en cache dans static/og/."""
    cache = RACINE / "static" / "og" / f"{a['slug']}.png"
    signature = RACINE / "static" / "og" / f"{a['slug']}.txt"
    cle = f"{a['title']}|{a['category']}|v2"
    if not (cache.exists() and signature.exists() and signature.read_text(encoding="utf-8") == cle):
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            print(f"  alerte : Pillow absent, image de partage non générée pour {a['slug']}")
            return None
        polices = RACINE / "static" / "fonts"
        demi = ImageFont.truetype(str(polices / "Inter-SemiBold.otf"), 30)
        img = Image.new("RGB", (1200, 630), "#fffef8")
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, 1200, 14], fill="#ffe24a")
        d.text((80, 80), a["category"].upper(), font=demi, fill="#d1243b")
        for taille in (68, 58, 50, 44):
            gras = ImageFont.truetype(str(polices / "Inter-ExtraBold.otf"), taille)
            lignes, ligne = [], ""
            for mot in a["title"].split():
                essai = f"{ligne} {mot}".strip()
                if d.textlength(essai, font=gras) <= 1040:
                    ligne = essai
                else:
                    lignes.append(ligne); ligne = mot
            lignes.append(ligne)
            if len(lignes) * taille * 1.18 <= 380:
                break
        y = 140
        for l in lignes:
            d.text((80, y), l, font=gras, fill="#1b1b1f"); y += int(taille * 1.18)
        d.line([80, 540, 1120, 540], fill="#1b1b1f", width=3)
        nom = ImageFont.truetype(str(polices / "Inter-ExtraBold.otf"), 34)
        d.text((80, 562), "Fin de Mois", font=nom, fill="#1b1b1f")
        d.text((1120, 566), "le budget étudiant expliqué simplement", font=demi, fill="#5d5f68", anchor="ra")
        cache.parent.mkdir(exist_ok=True)
        img.save(cache, optimize=True)
        signature.write_text(cle, encoding="utf-8")
    shutil.copy(cache, dossier / "partage.png")
    return f"{BASE}/{a['slug']}/partage.png"

def page(titre, desc, url, contenu, schemas=(), image=None, type_og="website"):
    sch = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in schemas)
    og_img = (f'<meta property="og:image" content="{image}">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta name="twitter:card" content="summary_large_image">') if image else '<meta name="twitter:card" content="summary">'
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
<meta property="og:type" content="{type_og}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{NOM}">
<meta property="og:locale" content="fr_FR">
{og_img}
<link rel="icon" href="{BASE}/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700;800&family=Literata:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{BASE}/style.css">
{sch}
</head>
<body>
<header class="tete"><div class="w">
<a class="logo" href="{BASE}/" aria-label="Fin de Mois, accueil"><svg class="logo-mark" viewBox="0 0 48 48" aria-hidden="true"><g transform="rotate(-6 24 24)"><rect x="7" y="9" width="34" height="33" rx="4" fill="#fff" stroke="currentColor" stroke-width="2.6"/><path d="M7 13a4 4 0 0 1 4-4h26a4 4 0 0 1 4 4v5H7z" fill="currentColor"/><rect x="15" y="5" width="3.2" height="8" rx="1.6" fill="currentColor"/><rect x="29.8" y="5" width="3.2" height="8" rx="1.6" fill="currentColor"/><text x="24" y="36.5" text-anchor="middle" font-family="Bricolage Grotesque,system-ui,sans-serif" font-weight="800" font-size="16" fill="currentColor" letter-spacing="-.5">31</text></g><path class="logo-cercle" d="M12.5 29.5c1-6.8 9.6-9.6 16.6-8.4 7.3 1.3 10.4 6.6 8.6 11.4-1.9 5-9.7 7.4-16.4 6.3C14.6 37.7 11.2 33.9 12.8 28.6c.9-3 3.4-4.9 6-6" fill="none" stroke="#d1243b" stroke-width="2.2" stroke-linecap="round"/></svg><span class="logo-nom">Fin de <span class="logo-mois">Mois</span></span></a>
<nav><a href="{BASE}/#articles">Articles</a><a href="{BASE}/a-propos/">À propos</a></nav>
</div></header>
{contenu}
<footer><div class="w"><span>Fin de Mois, le budget étudiant expliqué simplement.</span><span>Infos vérifiées sur les sources officielles · <a href="{BASE}/a-propos/">Comment on vérifie</a></span></div></footer>
</body>
</html>"""

def fil(*etapes):
    """Fil d'Ariane visible : liste de (nom, url) ; le dernier élément n'est pas un lien."""
    morceaux = [f'<a href="{u}">{html.escape(n)}</a>' for n, u in etapes[:-1]] + [f'<span>{html.escape(etapes[-1][0])}</span>']
    return '<nav class="fil" aria-label="Fil d\'Ariane">' + ' <span aria-hidden="true">›</span> '.join(morceaux) + '</nav>'

def schema_fil(*etapes):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(etapes)]}

def carte(a):
    return f"""<a class="art" href="{BASE}/{a['slug']}/"><time datetime="{a['date']}">{date_fr(a['date'])}</time>
<div><span class="cat">{html.escape(a['category'])}</span><h3>{html.escape(a['title'])}</h3><p>{html.escape(a['description'])}</p></div></a>"""

def lire_tous():
    arts, erreurs = [], []
    for p in sorted((RACINE / "articles").glob("*.md")):
        try:
            arts.append(lire(p))
        except Exception:
            erreurs.append(f"articles/{p.name} : en-tête illisible (il doit commencer par ---, puis title/description/date/category, puis ---)")
    return arts, erreurs

def construire():
    arts, erreurs = lire_tous()
    if not erreurs:
        e, alertes = verifier(arts)
        erreurs += e
        for x in alertes:
            print(f"  alerte : {x}")
    if erreurs:
        print("ÉCHEC : le site n'a pas été généré. À corriger :", file=sys.stderr)
        for x in erreurs:
            print(f"  - {x}", file=sys.stderr)
        sys.exit(1)

    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    SORTIE.mkdir()
    shutil.copy(RACINE / "static" / "style.css", SORTIE / "style.css")
    shutil.copy(RACINE / "static" / "favicon.svg", SORTIE / "favicon.svg")
    (SORTIE / ".nojekyll").write_text("")

    arts.sort(key=lambda a: (a["date"], a["slug"]), reverse=True)
    cats = [c for c in CATEGORIES if any(a["category"] == c for a in arts)]
    accueil_fil = ("Accueil", f"{BASE}/")
    editeur = {"@type": "Organization", "name": NOM, "url": f"{BASE}/"}

    for a in arts:
        url = f"{BASE}/{a['slug']}/"
        d = SORTIE / a["slug"]; d.mkdir()
        image = image_partage(a, d)
        verifie = a.get("updated", a["date"])
        autres = sorted([b for b in arts if b["slug"] != a["slug"]], key=lambda b: b["category"] != a["category"])[:3]
        aussi = ('<aside class="aussi"><h2>À lire aussi</h2><ul>' + "".join(f'<li><a href="{BASE}/{b["slug"]}/">{html.escape(b["title"])}</a></li>' for b in autres) + '</ul></aside>') if autres else ""
        etapes = (accueil_fil, (a["category"], url_cat(a["category"])), (a["title"], url))
        contenu = f"""<main class="article">
{fil(*etapes)}
<a class="cat" href="{url_cat(a['category'])}">{html.escape(a['category'])}</a>
<h1>{html.escape(a['title'])}</h1>
<p class="meta">Publié le {date_fr(a['date'])}<span class="verif">Infos vérifiées le {date_fr(verifie)}</span></p>
<div class="corps">{a['corps']}</div>
<p class="avert">Les montants et les règles peuvent changer : en cas de doute, la source officielle fait foi. <a href="{BASE}/a-propos/#erreur">Signaler une erreur</a></p>
{aussi}
<p style="margin-top:40px"><a href="{BASE}/">← Tous les articles</a></p>
</main>"""
        article = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"],
                   "description": a["description"], "datePublished": a["date"], "dateModified": verifie,
                   "inLanguage": "fr", "mainEntityOfPage": url, "author": editeur, "publisher": editeur}
        if image:
            article["image"] = image
        schemas = [article, schema_fil(*etapes)]
        q = faq(a["md"])
        if q:
            schemas.append({"@context": "https://schema.org", "@type": "FAQPage",
                            "mainEntity": [{"@type": "Question", "name": x, "acceptedAnswer": {"@type": "Answer", "text": r}} for x, r in q]})
        (d / "index.html").write_text(page(f"{a['title']} | {NOM}", a["description"], url, contenu, schemas, image, "article"), encoding="utf-8")

    puces = '<nav class="cats" aria-label="Catégories">' + "".join(f'<a href="{url_cat(c)}">{html.escape(c)}</a>' for c in cats) + "</nav>"

    for c in cats:
        url = url_cat(c)
        liste = [a for a in arts if a["category"] == c]
        n = len(liste)
        contenu = f"""<main class="w">
<section class="entete-cat">{fil(accueil_fil, (c, url))}
<h1>{html.escape(c)}</h1>
<p>{n} article{'s' if n > 1 else ''} vérifié{'s' if n > 1 else ''} sur les sources officielles.</p>
{puces}</section>
<section class="liste">{"".join(carte(a) for a in liste)}</section>
</main>"""
        desc = f"Les articles Fin de Mois de la catégorie {c} : montants à jour, démarches et pièges à éviter pour les étudiants."
        d = SORTIE / "categorie" / slugifier(c); d.mkdir(parents=True)
        (d / "index.html").write_text(page(f"{c} : budget étudiant | {NOM}", desc, url, contenu, [schema_fil(accueil_fil, (c, url))]), encoding="utf-8")

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
<section class="liste" id="articles"><h2>Derniers articles</h2>{puces}{"".join(carte(a) for a in arts)}</section>
</main>"""
    site = {"@context": "https://schema.org", "@type": "WebSite", "name": NOM, "url": f"{BASE}/", "inLanguage": "fr"}
    (SORTIE / "index.html").write_text(page(f"{NOM} : le budget étudiant expliqué simplement", "Aides étudiantes, bourses, APL, bons plans : les montants à jour et les démarches expliquées simplement.", f"{BASE}/", accueil, [site]), encoding="utf-8")

    apropos = f"""<main class="article"><h1>À propos</h1><div class="corps">
<p>Fin de Mois explique simplement les aides, les démarches et les bons plans qui comptent quand on est étudiant.</p>
<h2>Comment les infos sont vérifiées</h2>
<p>Chaque montant et chaque date viennent des sources officielles (service-public.fr, caf.fr, lescrous.fr, etudiant.gouv.fr, legifrance.gouv.fr…) ou, à défaut, de deux sources sérieuses récentes. Si une information ne peut pas être confirmée, elle n'est pas publiée. Les sources sont listées en bas de chaque article, avec la date de la dernière vérification.</p>
<p>Les montants peuvent évoluer : en cas de doute, la source officielle fait toujours foi. Fin de Mois donne des informations générales, pas de conseil financier personnalisé.</p>
<h2 id="erreur">Signaler une erreur</h2>
<p>Un montant a changé ou une règle n'est plus à jour ? <a href="https://github.com/ingaaal/site-auto/issues/new" rel="nofollow noopener">Signale-le ici</a> (compte GitHub nécessaire), en indiquant l'article et la source officielle. L'article sera corrigé et sa date de vérification mise à jour.</p>
</div></main>"""
    (SORTIE / "a-propos").mkdir()
    (SORTIE / "a-propos" / "index.html").write_text(page(f"À propos | {NOM}", "Qui écrit Fin de Mois, comment les articles sont vérifiés et comment signaler une erreur.", f"{BASE}/a-propos/", apropos), encoding="utf-8")

    page404 = f"""<main class="article"><h1>Page introuvable</h1><div class="corps">
<p>Cette page n'existe pas ou a changé d'adresse.</p>
<p><a href="{BASE}/">Retour à l'accueil</a> ou choisis une catégorie :</p></div>{puces}</main>"""
    (SORTIE / "404.html").write_text(page(f"Page introuvable | {NOM}", "Cette page n'existe pas ou a changé d'adresse.", f"{BASE}/", page404).replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1), encoding="utf-8")

    plus_recent = max(a.get("updated", a["date"]) for a in arts) if arts else date.today().isoformat()
    lastmod = {f"{BASE}/": plus_recent, f"{BASE}/a-propos/": plus_recent}
    lastmod.update({f"{BASE}/{a['slug']}/": a.get("updated", a["date"]) for a in arts})
    lastmod.update({url_cat(c): max(a.get("updated", a["date"]) for a in arts if a["category"] == c) for c in cats})
    sm = "".join(f"<url><loc>{u}</loc><lastmod>{m}</lastmod></url>" for u, m in lastmod.items())
    (SORTIE / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    (SORTIE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    print(f"{len(arts)} articles et {len(cats)} catégories générés dans docs/")

if __name__ == "__main__":
    construire()
