"""Verifie que toutes les pages portent le pied de page de l'accueil.

Compare la liste des liens, pas une chaine temoin : un marqueur unique
casse des qu'on retire un bloc, ce qui est arrive avec la ligne des villes.
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IGNORE = ("mockups", ".git")
HORS_SITE = ("google", "design-2026.html", "hero-", "mockups-hero.html", "cockpit-demo.html")

def pied(html):
    m = re.search(r"<footer[^>]*>.*?</footer>", html, re.S)
    return m.group(0) if m else None

def liens(bloc):
    return tuple(sorted(set(re.findall(r'href="([^"]+)"', bloc))))

ref = liens(pied(open(os.path.join(RACINE, "index.html"), encoding="utf-8").read()))
print(f"  reference : {len(ref)} liens distincts dans le pied de page de l'accueil")

ecarts, sans, ouvert = [], [], []
for d, sous, noms in os.walk(RACINE):
    sous[:] = [x for x in sous if x not in IGNORE]
    for n in noms:
        if not n.endswith(".html"):
            continue
        rel = os.path.relpath(os.path.join(d, n), RACINE).replace(os.sep, "/")
        if rel == "index.html" or any(k in rel for k in HORS_SITE):
            continue
        html = open(os.path.join(d, n), encoding="utf-8").read()
        if html.count("<footer") != html.count("</footer>"):
            ouvert.append(rel)
        p = pied(html)
        if p is None:
            sans.append(rel)
        elif liens(p) != ref:
            manquants = set(ref) - set(liens(p))
            surplus = set(liens(p)) - set(ref)
            ecarts.append((rel, len(manquants), len(surplus)))

for rel in sans:
    print(f"  [!!] {rel} : aucun pied de page")
for rel in ouvert:
    print(f"  [!!] {rel} : balise <footer> non fermee")
for rel, m, s in ecarts:
    print(f"  [!!] {rel} : {m} lien(s) manquant(s), {s} en trop")

if sans or ouvert or ecarts:
    sys.exit(1)
print("  [OK] toutes les pages portent le pied de page de l'accueil")
