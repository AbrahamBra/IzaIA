"""Harmonise la graphie de la marque dans les seules metadonnees.

Perimetre volontairement etroit : <title>, <meta name="description">,
et les <meta property="og:*"> / "twitter:*".

Le JSON-LD est EXCLU, et ce n'est pas un oubli. Les blocs FAQPage citent
mot pour mot des questions et des reponses visibles sur la page, et Google
exige cette correspondance. Changer la graphie dans le schema sans la
changer dans le corps de la page creerait justement la divergence que le
schema est cense refleter. La graphie du corps des pages releve d'une
relecture editoriale, pas d'un script.
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RETENUE = "IzaIA"
DIVERGENTES = re.compile(r"\b(?:IZAIA|Izaia)\b")

LIGNE_META = re.compile(
    r'^\s*(?:<title>|<meta\s+(?:name|property)="(?:description|og:[a-z:]+|twitter:[a-z:]+)")'
)

racine = os.getcwd()
total, fichiers = 0, 0
for dossier, sous, noms in os.walk(racine):
    sous[:] = [d for d in sous if d not in (".git", "mockups", "docs", "verif")]
    for nom in noms:
        if not nom.endswith(".html"):
            continue
        chemin = os.path.join(dossier, nom)
        lignes = open(chemin, encoding="utf-8").read().split("\n")
        n = 0
        for i, ligne in enumerate(lignes):
            if LIGNE_META.match(ligne):
                nouvelle, k = DIVERGENTES.subn(RETENUE, ligne)
                if k:
                    lignes[i] = nouvelle
                    n += k
        if n:
            open(chemin, "w", encoding="utf-8").write("\n".join(lignes))
            print(f"  {os.path.relpath(chemin, racine)} : {n} remplacement(s)")
            total += n
            fichiers += 1
print(f"\n{total} remplacement(s) dans {fichiers} fichier(s).")
