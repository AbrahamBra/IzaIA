# -*- coding: utf-8 -*-
"""Lit une page comme un robot : HTML brut, sans script ni feuille de style."""
import html
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def texte(fragment):
    t = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", " ", fragment, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def auditer(chemin):
    p = io.open(chemin, encoding="utf-8").read()
    print("=" * 70)
    print(chemin)
    titre = re.search(r"<title>(.*?)</title>", p, re.S).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)"', p).group(1)
    print("title        %3d car. | %s" % (len(html.unescape(titre)), html.unescape(titre)))
    print("description  %3d car. | %s" % (len(html.unescape(desc)), html.unescape(desc)))
    print("canonical    |", re.search(r'<link rel="canonical" href="([^"]*)"', p).group(1))
    print("robots meta  |", re.findall(r'<meta name="robots"[^>]*>', p) or "aucune (indexable)")
    print("lang         |", re.search(r'<html lang="([^"]*)"', p).group(1))
    print("og:type      |", re.search(r'og:type" content="([^"]*)"', p).group(1))

    corps = p[p.index("<body"):]
    principal = corps[corps.index('<section class="page-hero">'):corps.index('<footer class="site">')]

    # Hierarchie des titres
    titres = re.findall(r"<h([1-6])[^>]*>(.*?)</h\1>", principal, re.S)
    niveaux = [int(n) for n, _ in titres]
    print("titres       | h1=%d h2=%d h3=%d h4=%d" % tuple(niveaux.count(i) for i in (1, 2, 3, 4)))
    sauts = [(niveaux[i - 1], niveaux[i]) for i in range(1, len(niveaux)) if niveaux[i] > niveaux[i - 1] + 1]
    print("sauts de niveau |", sauts or "aucun")
    for n, t in titres:
        if n in "12":
            print("   h%s %s" % (n, texte(t)))

    # Identifiants en double
    ids = re.findall(r'\sid="([^"]+)"', p)
    doubles = sorted(set(i for i in ids if ids.count(i) > 1))
    print("id en double |", doubles or "aucun")

    # Ce qu'un robot lit sans script
    t = texte(principal)
    mots = t.split()
    print("mots (corps) |", len(mots))
    print("contenu masque sans script |", len(re.findall(r"\shidden[\s>]", principal)), "element(s) hidden,",
          len(re.findall(r"display:\s*none", principal)), "display:none en ligne")
    print("100 premiers mots | " + " ".join(mots[:100]))

    # Reponse sous chaque h2 : les deux premieres phrases qui suivent
    print("--- sous chaque h2 (40 premiers mots)")
    morceaux = re.split(r"<h2[^>]*>", principal)[1:]
    for m in morceaux:
        h2, reste = m.split("</h2>", 1)
        print("   [%s] %s" % (texte(h2), " ".join(texte(reste).split()[:40])))

    # Donnees structurees
    print("--- JSON-LD")
    for bloc in re.findall(r'<script type="application/ld\+json">(.*?)</script>', p, re.S):
        d = json.loads(bloc)
        cles = [k for k in d if not k.startswith("@")]
        print("   %-15s %s" % (d["@type"], ", ".join(cles)))
        if d["@type"] == "FAQPage":
            for q in d["mainEntity"]:
                r = q["acceptedAnswer"]["text"]
                print("      Q %s (%d mots)" % (q["name"], len(r.split())))

    # Liens
    liens = re.findall(r'<a [^>]*href="([^"]+)"', principal)
    ext = sorted(set(l for l in liens if l.startswith("http") and "izaia" not in l and "zeeg" not in l))
    internes = sorted(set(l for l in liens if l.startswith("/")))
    print("liens sortants vers des sources |", len(ext))
    for l in ext:
        print("   ", l)
    print("liens internes |", internes)
    dates = re.findall(r"(?:Mis à jour|dateModified)[^<\"]{0,40}", p)
    print("dates        |", dates[:3])
    print("octets       |", len(p.encode("utf-8")))


for c in sys.argv[1:]:
    auditer(c)
