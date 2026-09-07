"""Ajoute les treize verticales au menu mobile du gabarit precedent.

Ce menu est un bloc ecrit a la main, distinct du nav-drop : etendre le
nav-drop ne l'avait pas touche, et les pages metier restaient hors de
portee sur telephone depuis ces dix-huit pages.

Refuse d'ecrire si le bloc source n'est pas reconnu au caractere pres.
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = os.getcwd()

VERTICALES = [
    ("expert-comptable",   "Expertise comptable"),
    ("avocat",             "Avocats"),
    ("notaire",            "Notariat"),
    ("cgp",                "Gestion de patrimoine"),
    ("banque",             "Banque"),
    ("assurance",          "Assurance"),
    ("syndic-copropriete", "Syndic &amp; copropriété"),
    ("collectivites",      "Collectivités"),
    ("clinique",           "Cliniques &amp; santé"),
    ("ehpad",              "EHPAD &amp; médico-social"),
    ("medecin",            "Médecins"),
    ("industrie",          "Industrie"),
    ("sur-mesure",         "Sur mesure (tous secteurs)"),
]

def source(p):
    return f'    <a href="{p}formation/" onclick="closeMobileMenu()">Formation</a>\n'

def cible(p):
    bloc = source(p)
    bloc += '    <span class="mobile-menu-label">Par métier</span>\n'
    for slug, libelle in VERTICALES:
        bloc += (f'    <a href="{p}{slug}/" class="mm-metier" '
                 f'onclick="closeMobileMenu()">{libelle}</a>\n')
    return bloc

pages = []
for dossier, sous, noms in os.walk(RACINE):
    sous[:] = [d for d in sous if d not in (".git", "mockups")]
    if "index.html" not in noms:
        continue
    chemin = os.path.join(dossier, "index.html")
    with open(chemin, encoding="utf-8") as fh:
        if 'class="mobile-menu"' in fh.read():
            pages.append(chemin)

print(f"{len(pages)} page(s) avec un menu mobile ecrit a la main.\n")

faites, ignorees = [], []
for chemin in sorted(pages):
    html = open(chemin, encoding="utf-8").read()
    if 'class="mm-metier"' in html:
        ignorees.append((chemin, "deja fait")); continue
    profondeur = os.path.relpath(chemin, RACINE).replace(os.sep, "/").count("/")
    p = "../" * profondeur
    src = source(p)
    if html.count(src) != 1:
        ignorees.append((chemin, f"{html.count(src)} bloc(s) pour le prefixe '{p}'"))
        continue
    open(chemin, "w", encoding="utf-8").write(html.replace(src, cible(p), 1))
    faites.append(chemin)

for c in faites:
    print(f"  modifiee  {os.path.relpath(c, RACINE)}")
for c, motif in ignorees:
    print(f"  IGNOREE   {os.path.relpath(c, RACINE)}  ({motif})")
print(f"\n{len(faites)} modifiee(s), {len(ignorees)} ignoree(s).")
