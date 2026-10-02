# -*- coding: utf-8 -*-
"""Assemble une page de dossier (expertise comptable, collectivites).

Reprend l'en-tete, le pied de page et les scripts de la page mere du dossier
(pour ne pas recopier a la main le menu ni l'image Qualiopi du pied), y insere
le corps redige a part (*-corps.html), et genere le bloc FAQPage a partir de
la FAQ visible. Les pages produites ne se modifient pas a la main : on modifie
le corps, puis on relance.

    python tools/dossiers/assembler.py reponse|agents|coll-reponse|coll-agents
"""
import html
import io
import json
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(ICI))
BASE = "https://www.izaia.fr"

CSS = {
    "sec-alt": ".sec-alt{background:var(--paper-soft)}",
    "prose": """.prose{max-width:70ch}
.prose p{margin-bottom:18px;font-size:17px;color:var(--txt)}
.prose p:last-child{margin-bottom:0}
.prose p.first{font-size:18.5px}""",
    "hero": """.hero-frag{
  color:var(--paper-txt-soft);font-size:19px;
  margin-top:18px;max-width:44ch;
}
.page-hero .kicker.on-dark{margin-bottom:6px}
.page-hero h1{max-width:24ch}
.hero-actions{display:flex;flex-wrap:wrap;gap:14px;margin-top:34px}""",
    "signature": ".page-hero p.signature{font-size:14.5px;margin-top:22px;color:var(--paper-txt-soft)}",
    "know": """.know{display:grid;gap:0;margin-top:40px;border-top:1px solid var(--line)}
.know-item{
  padding:30px 0;border-bottom:1px solid var(--line);
  display:grid;grid-template-columns:minmax(0,26ch) minmax(0,1fr);gap:38px;
}
.know-item h3{
  font-size:20px;line-height:1.28;font-family:var(--serif);font-weight:500;
  scroll-margin-top:110px;
}
.know-item .kbody{min-width:0}
.know-item .kbody p{margin-bottom:14px;font-size:16.5px;color:var(--txt-soft)}
.know-item .kbody p:last-child{margin-bottom:0}
.know-item .kbody strong{color:var(--ink);font-weight:600}""",
    "klist": """.klist{list-style:none;display:grid;gap:9px;margin:0 0 14px}
.klist li{position:relative;padding-left:20px;font-size:16.5px;color:var(--txt-soft)}
.klist li::before{content:"\\2014";position:absolute;left:0;color:var(--gold)}""",
    "feux": """.feux{width:100%;border-collapse:collapse;margin:22px 0 4px;font-size:15px}
.feux th{
  text-align:left;font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--txt-soft);font-weight:700;padding:0 14px 10px 0;border-bottom:1px solid var(--line);
}
.feux td{padding:14px 14px 14px 0;border-bottom:1px solid var(--line);vertical-align:top;color:var(--txt-soft)}
.feux tr:last-child td{border-bottom:0}
.feux td:first-child{font-weight:700;color:var(--ink);white-space:nowrap}
.feux td:first-child::before{
  content:"";display:inline-block;width:9px;height:9px;border-radius:50%;
  margin-right:9px;vertical-align:middle;background:var(--pine);
}
.feux tr.orange td:first-child::before{background:var(--gold)}
.feux tr.rouge td:first-child::before{background:#9B3A2A}
.tablewrap{overflow-x:auto}
@media (max-width:520px){
  .feux thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
  .feux,.feux tbody,.feux tr,.feux td{display:block}
  .feux tr{padding:14px 0;border-bottom:1px solid var(--line)}
  .feux tr:last-child{border-bottom:0}
  .feux td{padding:2px 0;border-bottom:0}
  .feux td:nth-child(2){font-weight:600;color:var(--txt)}
}""",
    "situ": """.situations{display:grid;gap:0;margin-top:14px}
.situ{padding:26px 0;border-bottom:1px solid var(--line)}
.situ:last-child{border-bottom:0}
.situ b{display:block;font-size:17.5px;color:var(--ink);font-family:var(--serif);font-weight:500;margin-bottom:7px}
.situ span{font-size:16px;color:var(--txt-soft)}""",
    "limites": """.limites{list-style:none;display:grid;gap:16px;margin-top:26px;text-align:left}
.limites li{
  padding-left:34px;position:relative;font-size:16px;color:var(--paper-txt-soft);
}
.limites li::before{
  content:"";position:absolute;left:0;top:.62em;width:18px;height:1.5px;background:var(--gold);
}
.limites b{color:var(--paper);font-weight:600}""",
    "aussi": """.aussi{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}
.aussi a{
  font-size:14.5px;font-weight:600;color:var(--pine);text-decoration:none;
  border:1px solid var(--line);border-radius:100px;padding:8px 16px;background:#fff;
  transition:border-color .18s ease,color .18s ease;
}
.aussi a:hover{border-color:var(--pine)}""",
    "cas": """/* ---- Exemples : pastilles de filtre et cartes ---- */
.filtres{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 6px}
.filtres a{
  font-size:14.5px;font-weight:600;color:var(--pine);text-decoration:none;cursor:pointer;
  border:1px solid var(--line);border-radius:100px;padding:8px 16px;background:#fff;
  transition:border-color .18s ease,background .18s ease,color .18s ease;
}
.filtres a span{font-weight:500;color:var(--txt-soft);margin-left:4px}
.filtres a:hover{border-color:var(--pine)}
.filtres a:focus-visible{outline:3px solid var(--gold);outline-offset:3px}
.filtres.actifs a[aria-pressed="true"]{background:var(--pine);border-color:var(--pine);color:var(--paper)}
.filtres.actifs a[aria-pressed="true"] span{color:var(--paper-txt-soft)}
.filtres{scroll-margin-top:calc(var(--entete,76px) + 64px)}
.famille{font-size:clamp(22px,2.4vw,27px);margin:44px 0 18px}
.exemples{display:grid;grid-template-columns:minmax(0,1fr);gap:14px;align-items:start}
.exemple{
  background:#fff;border:1px solid var(--line);border-radius:var(--radius);
  padding:20px 22px;
}
.exemple summary{list-style:none;position:relative;cursor:pointer;padding-right:30px}
.exemple summary::-webkit-details-marker{display:none}
.exemple summary::after{
  content:"+";position:absolute;right:0;top:50%;transform:translateY(-50%);
  font-size:22px;line-height:1;color:var(--pine);
}
.exemple[open] summary::after{content:"\\2013"}
.exemple summary:focus-visible{outline:3px solid var(--gold);outline-offset:6px;border-radius:6px}
.exemple .num{display:block;font-size:12px;font-weight:700;letter-spacing:.16em;color:var(--gold-ink)}
.exemple h4{font-family:var(--serif);font-weight:500;font-size:18px;line-height:1.28;color:var(--ink);margin:4px 0 0}
.cas{display:grid;gap:12px;margin:16px 0 2px}
@media (min-width:700px){
  .exemples{grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;align-items:stretch}
  .exemple{padding:24px 26px 26px}
  .exemple summary{cursor:default;pointer-events:none;padding-right:0}
  .exemple summary::after{content:none}
  .exemple h4{font-size:19px}
}
.cas dt{font-size:11.5px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--txt-soft);margin-bottom:2px}
.cas dd{margin:0;font-size:15.5px;color:var(--txt-soft)}
.cas div:nth-child(2) dt{color:var(--gold-ink)}
.cas div:nth-child(2) dd{color:var(--txt)}
.cas .prerequis{border-top:1px dashed var(--line);padding-top:12px}
.cas .prerequis dd,.cas .savoir dd{font-size:14.5px}""",
    "dossier": """/* ---- Ligne « Dans ce dossier », en bas du bandeau ---- */
.dossier{
  margin-top:44px;padding-top:22px;border-top:1px solid var(--line-light);
  display:flex;flex-wrap:wrap;align-items:center;gap:12px 22px;
}
.dossier-titre{
  font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);
}
.dossier ul{list-style:none;display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0}
.dossier a{
  display:block;font-size:14.5px;font-weight:600;text-decoration:none;
  color:var(--paper);border:1px solid var(--line-light);border-radius:100px;padding:8px 16px;
  transition:border-color .18s ease;
}
.dossier a:hover{border-color:var(--paper)}
.dossier a:focus-visible{outline:3px solid var(--gold);outline-offset:3px}
.dossier a[aria-current="page"]{background:var(--paper);color:var(--ink);border-color:var(--paper)}""",
    "sommaire": """/* ---- Sommaire collant, sous l'en-tete ---- */
.sommaire{
  position:sticky;top:var(--entete,76px);z-index:90;
  background:var(--paper);border-bottom:1px solid var(--line);
}
.sommaire ul{
  list-style:none;display:flex;gap:26px;margin:0;padding:0;
  overflow-x:auto;scrollbar-width:none;white-space:nowrap;
}
.sommaire ul::-webkit-scrollbar{display:none}
.sommaire a{
  display:block;padding:14px 0 12px;font-size:14.5px;font-weight:600;
  color:var(--txt-soft);text-decoration:none;border-bottom:2px solid transparent;
}
.sommaire a:hover{color:var(--ink)}
.sommaire a:focus-visible{outline:3px solid var(--gold);outline-offset:-3px}
.sommaire a[aria-current="true"]{color:var(--ink);border-bottom-color:var(--gold)}
/* Ecran peu haut (telephone a l'horizontale) : le sommaire ne colle plus. */
@media (max-height:520px){
  .sommaire{position:static}
}""",
    "tab": """/* ---- Tableau comparatif ---- */
.tab{width:100%;border-collapse:collapse;margin:22px 0 4px;font-size:15px}
.tab th{
  text-align:left;font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--txt-soft);font-weight:700;padding:0 14px 10px 0;border-bottom:1px solid var(--line);
}
.tab td{padding:14px 14px 14px 0;border-bottom:1px solid var(--line);vertical-align:top;color:var(--txt-soft)}
.tab tr:last-child td{border-bottom:0}
.tab td:first-child{font-weight:700;color:var(--ink)}
.tab td:last-child{color:var(--txt)}
.tablewrap{overflow-x:auto}
@media (max-width:620px){
  .tab thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
  .tab,.tab tbody,.tab tr,.tab td{display:block}
  .tab tr{padding:14px 0;border-bottom:1px solid var(--line)}
  .tab tr:last-child{border-bottom:0}
  .tab td{padding:3px 0;border-bottom:0}
  .tab td[data-th]::before{
    content:attr(data-th) " : ";font-size:11.5px;font-weight:700;letter-spacing:.1em;
    text-transform:uppercase;color:var(--txt-soft);
  }
}""",
    "ancres": "section[id],h3[id]{scroll-margin-top:calc(var(--entete,76px) + 64px)}",
    "mobile": """@media (max-width:900px){
  .know-item{grid-template-columns:minmax(0,1fr);gap:12px}
  .sommaire ul{gap:20px}
}
.maj{font-size:13.5px;color:var(--txt-soft);margin-top:22px}""",
}

DOSSIERS = {
    "ec": {
        "nom": "Dossier expertise comptable",
        "mere": os.path.join("expert-comptable", "index.html"),
        "liens": [
            ("La formation", "/expert-comptable/"),
            ("Les agents IA", "/expert-comptable/agents-ia/"),
            ("ChatGPT et secret professionnel", "/expert-comptable/blog/chatgpt-expert-comptable.html"),
        ],
    },
    "coll": {
        "nom": "Dossier collectivités",
        "mere": os.path.join("collectivites", "index.html"),
        "liens": [
            ("La formation", "/collectivites/"),
            ("Les agents IA", "/collectivites/agents-ia/"),
            ("L'obligation de former", "/collectivites/obligation-formation-ia/"),
        ],
    },
}

PAGES = {
    "reponse": {
        "dossier": "ec",
        "corps": "ec-reponse-corps.html",
        "sortie": os.path.join("expert-comptable", "blog", "chatgpt-expert-comptable.html"),
        "url": BASE + "/expert-comptable/blog/chatgpt-expert-comptable.html",
        "styles": "../../styles/",
        "og_type": "article",
        "title": "ChatGPT ou une autre IA en cabinet comptable ? | IzaIA",
        "description": "Oui, dans la limite du secret professionnel. La règle en trois catégories, les textes qui la fondent, la position de l'Ordre et trois cas tranchés.",
        "og_description": "Oui, sous conditions. La limite est celle du secret professionnel, et elle tient dans un tableau.",
        "css": ["sec-alt", "prose", "hero", "signature", "klist", "feux", "situ", "limites", "dossier", "sommaire", "ancres"],
        "sommaire": [("Réponse", "reponse"), ("La règle", "tableau"), ("Le droit", "texte"),
                     ("L'outil", "abonnement"), ("Trois cas", "cas"), ("Questions", "faq"),
                     ("Sources", "sources")],
        "fil": [("Accueil", BASE + "/"), ("Expertise comptable", BASE + "/expert-comptable/"),
                ("ChatGPT et secret professionnel", None)],
    },
    "agents": {
        "dossier": "ec",
        "catalogue": ("Exemples d'agents IA pour un cabinet d'expertise comptable", 17),
        "corps": "ec-agents-corps.html",
        "sortie": os.path.join("expert-comptable", "agents-ia", "index.html"),
        "url": BASE + "/expert-comptable/agents-ia/",
        "styles": "../../styles/",
        "og_type": "website",
        "title": "Agents IA pour les cabinets d'expertise comptable | IzaIA",
        "description": "Relance des pièces, tri de la messagerie, pré-saisie, paie, comptes rendus : dix-sept exemples d'agents IA pour un cabinet, relus par vos équipes.",
        "og_description": "Construits sur vos procédures. Branchés sur vos outils, dans un périmètre écrit. Rien n'est envoyé sans relecture.",
        "css": ["sec-alt", "prose", "hero", "know", "situ", "cas", "limites", "aussi", "dossier", "sommaire", "ancres", "mobile"],
        "sommaire": [("À savoir", "savoir"), ("Exemples", "cas"), ("Méthode", "methode"),
                     ("Limites", "limites"), ("Prix", "prix"), ("Questions", "faq")],
        "fil": [("Accueil", BASE + "/"), ("Expertise comptable", BASE + "/expert-comptable/"),
                ("Agents IA", None)],
    },
    "coll-reponse": {
        "dossier": "coll",
        "corps": "coll-reponse-corps.html",
        "sortie": os.path.join("collectivites", "obligation-formation-ia", "index.html"),
        "url": BASE + "/collectivites/obligation-formation-ia/",
        "styles": "../../styles/",
        "og_type": "article",
        "title": "Collectivités : faut-il former les agents à l'IA ? | IzaIA",
        "description": "L'article 4 du règlement européen sur l'IA, réécrit en juillet 2026, demande des mesures, sans durée ni attestation imposées. Ce que cela change en mairie.",
        "og_description": "Une collectivité est obligée d'agir, depuis le 2 février 2025. L'article 4 n'impose ni durée, ni attestation, ni niveau à atteindre.",
        "css": ["sec-alt", "prose", "hero", "signature", "klist", "tab", "situ", "limites", "dossier", "sommaire", "ancres"],
        "sommaire": [("Réponse", "reponse"), ("Le texte", "texte"), ("Qui est visé", "qui"),
                     ("Les mesures", "mesures"), ("Le risque", "risque"), ("Par où commencer", "commencer"),
                     ("Questions", "faq"), ("Sources", "sources")],
        "fil": [("Accueil", BASE + "/"), ("Collectivités", BASE + "/collectivites/"),
                ("Obligation de former les agents à l'IA", None)],
    },
    "coll-agents": {
        "dossier": "coll",
        "catalogue": ("Exemples d'agents IA pour une collectivité territoriale", 15),
        "corps": "coll-agents-corps.html",
        "sortie": os.path.join("collectivites", "agents-ia", "index.html"),
        "url": BASE + "/collectivites/agents-ia/",
        "styles": "../../styles/",
        "og_type": "website",
        "title": "Agents IA pour les mairies et les collectivités | IzaIA",
        "description": "Procès-verbaux de conseil, tri des demandes, dossiers de subvention, recherche dans les délibérations : quinze exemples d'agents IA pour une collectivité.",
        "og_description": "Choisis ou construits pour vos services. Un hébergement validé par votre délégué à la protection des données. Aucune réponse à un administré sans relecture.",
        "css": ["sec-alt", "prose", "hero", "know", "situ", "cas", "limites", "aussi", "dossier", "sommaire", "ancres", "mobile"],
        "sommaire": [("À savoir", "savoir"), ("Exemples", "cas"), ("Méthode", "methode"),
                     ("Limites", "limites"), ("Prix", "prix"), ("Questions", "faq")],
        "fil": [("Accueil", BASE + "/"), ("Collectivités", BASE + "/collectivites/"),
                ("Agents IA", None)],
    },
}


def texte(fragment):
    t = re.sub(r"<[^>]+>", "", fragment)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def faq_depuis(corps):
    questions = []
    faq = corps[corps.index('class="trio-faq"'):]
    faq = faq[:faq.index("</section>")]
    for bloc in re.findall(r"<details[^>]*>(.*?)</details>", faq, re.S):
        q = texte(re.search(r"<summary>(.*?)</summary>", bloc, re.S).group(1))
        r = " ".join(texte(p) for p in re.findall(r"<p>(.*?)</p>", bloc, re.S))
        questions.append({"@type": "Question", "name": q,
                          "acceptedAnswer": {"@type": "Answer", "text": r}})
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": questions}


def fil_ariane(fil):
    items = []
    for i, (nom, url) in enumerate(fil, 1):
        item = {"@type": "ListItem", "position": i, "name": nom}
        if url:
            item["item"] = url
        items.append(item)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def bloc_json(d):
    return ('<script type="application/ld+json">\n%s\n</script>'
            % json.dumps(d, ensure_ascii=False, indent=2))


def assembler(nom, entite):
    page = PAGES[nom]
    dossier = DOSSIERS[page["dossier"]]
    with io.open(os.path.join(SITE, dossier["mere"]), encoding="utf-8") as fh:
        mere = fh.read()
    # Bandeau d'annonce et en-tete, puis pied de page, reperes par leurs balises.
    entete = mere[mere.index('<div class="topbar">'):mere.index("</header>") + len("</header>")]
    pied = mere[mere.index('<footer class="site">'):mere.index("</footer>") + len("</footer>")]
    assert entete.lstrip().startswith('<div class="topbar">') and entete.rstrip().endswith("</header>")
    assert pied.startswith('<footer class="site">') and pied.rstrip().endswith("</footer>")
    pied = pied.replace('aria-label="IzaIA, accueil"', 'aria-label="IZAIA, accueil"')
    pied = pied.replace("Formation Flash Izaia", "Formation Flash IZAIA")

    with io.open(os.path.join(ICI, page["corps"]), encoding="utf-8") as fh:
        corps = fh.read().rstrip("\n")
    for _, ancre in page["sommaire"]:
        assert 'id="%s"' % ancre in corps, ancre
    items = "\n".join('      <li><a href="#%s">%s</a></li>' % (a, html.escape(l, quote=False))
                      for l, a in page["sommaire"])
    sommaire = ('<nav class="sommaire" aria-label="Sur cette page">\n  <div class="container">\n'
                '    <ul>\n%s\n    </ul>\n  </div>\n</nav>' % items)
    # La ligne « Dans ce dossier » ferme le bandeau : memes trois liens sur les
    # trois pages du dossier, la page en cours marquee.
    puces = "\n".join(
        '        <li><a href="%s"%s>%s</a></li>'
        % (url, ' aria-current="page"' if url == page["url"][len(BASE):] else "", libelle)
        for libelle, url in dossier["liens"])
    ligne = ('    <nav class="dossier" aria-label="%s">\n'
             '      <span class="dossier-titre">Dans ce dossier</span>\n'
             '      <ul>\n%s\n      </ul>\n    </nav>\n' % (dossier["nom"], puces))
    fin_hero = corps.index("</section>")
    coupe = corps.rindex("  </div>", 0, fin_hero)
    corps = corps[:coupe] + ligne + corps[coupe:]
    # Le sommaire se place juste apres le hero : premier </section> du corps.
    coupe = corps.index("</section>") + len("</section>")
    corps = corps[:coupe] + "\n\n" + sommaire + corps[coupe:]

    e = html.escape
    tete = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(description)s">
<link rel="canonical" href="%(url)s">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">

<meta property="og:type" content="%(og_type)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(og_description)s">
<meta property="og:url" content="%(url)s">
<meta property="og:site_name" content="IZAIA">
<meta property="og:locale" content="fr_FR">
<meta property="og:image" content="https://www.izaia.fr/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%(title)s">
<meta name="twitter:description" content="%(og_description)s">
<meta name="twitter:image" content="https://www.izaia.fr/og-image.jpg">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Public+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="%(styles)sizaia-2026.css">
<style>
/* ================================================================
   Complément à la charte 2026, repris de la page expertise comptable.
   N'introduit aucune couleur : tout vient des jetons existants.
================================================================ */
%(css)s
</style>
""" % {
        "title": e(page["title"], quote=True), "description": e(page["description"], quote=True),
        "og_description": e(page["og_description"], quote=True), "url": page["url"],
        "og_type": page["og_type"], "styles": page["styles"],
        "css": "\n".join(CSS[c] for c in page["css"]),
    }
    if page.get("catalogue"):
        nom_catalogue, attendu = page["catalogue"]
        entite = dict(entite)
        familles = []
        for bloc in re.findall(r'<div class="famille-bloc".*?(?=<div class="famille-bloc"|</section>)', corps, re.S):
            titre = texte(re.search(r'<h3[^>]*>(.*?)</h3>', bloc, re.S).group(1))
            offres = []
            for carte in re.findall(r'<details class="exemple".*?</details>', bloc, re.S):
                nom_ex = texte(re.search(r'<h4>(.*?)</h4>', carte, re.S).group(1))
                agent = texte(re.findall(r'<dd>(.*?)</dd>', carte, re.S)[1])
                offres.append({"@type": "Offer", "itemOffered": {
                    "@type": "Service", "name": nom_ex, "description": agent}})
            familles.append({"@type": "OfferCatalog", "name": titre, "itemListElement": offres})
        assert sum(len(f["itemListElement"]) for f in familles) == attendu
        entite["hasOfferCatalog"] = {
            "@type": "OfferCatalog",
            "name": nom_catalogue,
            "itemListElement": familles,
        }
    blocs = [bloc_json(entite), bloc_json(faq_depuis(corps)), bloc_json(fil_ariane(page["fil"]))]
    with io.open(os.path.join(ICI, "page.js"), encoding="utf-8") as fh:
        script = fh.read().rstrip("\n")
    fin = ('\n<script>\n%s\n</script>\n<script src="%sizaia-2026.js"></script>\n\n<script src="%snav.js"></script>\n</body>\n</html>\n'
           % (script, page["styles"], page["styles"]))
    sortie = (tete + "\n".join(blocs) + "\n</head>\n<body>\n\n" + entete + "\n\n" + corps
              + "\n" + pied + "\n" + fin)
    cible = os.path.join(SITE, page["sortie"])
    os.makedirs(os.path.dirname(cible), exist_ok=True)
    with io.open(cible, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(sortie)
    print("ecrit", cible, len(sortie), "caracteres")


ENTITES = {
    "reponse": {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Peut-on utiliser ChatGPT ou une autre IA dans un cabinet d'expertise comptable ?",
        "description": PAGES["reponse"]["description"],
        "author": {"@type": "Person", "name": "Abraham Brakha"},
        "publisher": {"@type": "Organization", "name": "IZAIA", "url": BASE},
        "datePublished": "2026-03-14",
        "dateModified": "2026-10-02",
        "mainEntityOfPage": PAGES["reponse"]["url"],
        "inLanguage": "fr-FR",
        "about": ["Secret professionnel de l'expert-comptable", "IA générative", "RGPD"],
        "citation": [
            "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000033678954",
            "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006417945",
            "https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre4#Article28",
            "https://www.cnil.fr/fr/les-questions-reponses-de-la-cnil-sur-lutilisation-dun-systeme-dia-generative",
            "https://www.experts-comptables.fr/travaux-data-et-ia",
        ],
    },
}

ENTITES["agents"] = {
    "@context": "https://schema.org",
    "@type": "Service",
    "name": "Agents IA pour les cabinets d'expertise comptable",
    "serviceType": "Développement d'agents IA sur mesure",
    "description": PAGES["agents"]["description"],
    "url": PAGES["agents"]["url"],
    "provider": {"@type": "Organization", "name": "IZAIA", "url": BASE},
    "areaServed": {"@type": "Country", "name": "France"},
    "audience": {"@type": "Audience", "audienceType": "Cabinets d'expertise comptable"},
}

ENTITES["coll-reponse"] = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Une collectivité est-elle obligée de former ses agents à l'IA ?",
    "description": PAGES["coll-reponse"]["description"],
    "author": {"@type": "Person", "name": "Abraham Brakha"},
    "publisher": {"@type": "Organization", "name": "IZAIA", "url": BASE},
    "datePublished": "2026-10-02",
    "dateModified": "2026-10-02",
    "mainEntityOfPage": PAGES["coll-reponse"]["url"],
    "inLanguage": "fr-FR",
    "about": ["Règlement européen sur l'intelligence artificielle", "Maîtrise de l'IA",
              "Collectivités territoriales", "Formation des agents territoriaux"],
    "citation": [
        "https://eur-lex.europa.eu/legal-content/FR/TXT/HTML/?uri=OJ:L_202401689",
        "https://eur-lex.europa.eu/legal-content/FR/TXT/HTML/?uri=OJ:L_202601744",
        "https://digital-strategy.ec.europa.eu/en/faqs/ai-literacy-questions-answers",
        "https://www.cnil.fr/fr/les-questions-reponses-de-la-cnil-sur-lutilisation-dun-systeme-dia-generative",
        "https://www.cnfpt.fr/se-former/decouvrir-offres-thematiques/lintelligence-artificielle/se-former-a-lia/national",
    ],
}

ENTITES["coll-agents"] = {
    "@context": "https://schema.org",
    "@type": "Service",
    "name": "Agents IA pour les mairies et les collectivités",
    "serviceType": "Choix, paramétrage et développement d'outils d'IA sur mesure",
    "description": PAGES["coll-agents"]["description"],
    "url": PAGES["coll-agents"]["url"],
    "provider": {"@type": "Organization", "name": "IZAIA", "url": BASE},
    "areaServed": {"@type": "Country", "name": "France"},
    "audience": {"@type": "Audience", "audienceType": "Communes, intercommunalités et syndicats"},
}

if __name__ == "__main__":
    assembler(sys.argv[1], ENTITES[sys.argv[1]])
