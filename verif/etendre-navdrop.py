"""Étend le nav-drop « Par métier » de 3 à 13 verticales.

Ne modifie qu'un bloc source reconnu au caractère près. Toute page dont
le nav-drop diverge est signalée et laissée intacte : sur ce dépôt, mieux
vaut 3 pages à regarder à la main qu'une substitution approximative.
"""
import os, re, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
]

def source(prefixe):
    """Le bloc tel qu'il existe aujourd'hui, pour un préfixe donné.

    L'absence de saut de ligne avant <div class="nav-drop-sep"> est
    authentique (voir tarif/index.html) : reprise ici au caractère près.
    """
    return (
        f'              <a href="{prefixe}avocat/">Avocat</a>\n'
        f'              <a href="{prefixe}expert-comptable/">Expert-comptable</a>'
        f'              <div class="nav-drop-sep"></div>\n'
    )

def cible(prefixe):
    return "".join(
        f'              <a href="{prefixe}{slug}/">{libelle}</a>\n'
        for slug, libelle in VERTICALES
    ) + '              <div class="nav-drop-sep"></div>\n'

# Les pages porteuses d'un nav-drop « Par métier ». Le libellé compte :
# sante/index.html a un nav-drop « Santé », qui n'est pas notre affaire.
pages = []
for dossier, _, fichiers in os.walk(RACINE):
    if "mockups" in dossier or ".git" in dossier:
        continue
    if "index.html" not in fichiers:
        continue
    chemin = os.path.join(dossier, "index.html")
    with open(chemin, encoding="utf-8") as fh:
        contenu = fh.read()
    if re.search(r'<span class="nav-drop-label">Par m[eé]tier</span>', contenu):
        pages.append(chemin)

print(f"{len(pages)} page(s) avec un nav-drop « Par métier ».\n")

modifiees, ignorees = [], []
for chemin in sorted(pages):
    with open(chemin, encoding="utf-8") as fh:
        html = fh.read()
    # Profondeur du fichier par rapport à la racine → préfixe relatif.
    profondeur = os.path.relpath(chemin, RACINE).replace(os.sep, "/").count("/")
    prefixe = "../" * profondeur
    src = source(prefixe)
    if html.count(src) != 1:
        ignorees.append((chemin, f"{html.count(src)} bloc(s) source pour le prefixe '{prefixe}'"))
        continue
    with open(chemin, "w", encoding="utf-8") as fh:
        fh.write(html.replace(src, cible(prefixe)))
    modifiees.append(chemin)

for c in modifiees:
    print(f"  modifiee  {os.path.relpath(c, RACINE)}")
for c, motif in ignorees:
    print(f"  IGNOREE   {os.path.relpath(c, RACINE)}  ({motif})")

print(f"\n{len(modifiees)} modifiee(s), {len(ignorees)} ignoree(s).")
sys.exit(1 if ignorees else 0)
