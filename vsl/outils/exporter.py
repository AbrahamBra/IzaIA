"""Exporte la page de vente hors du site.

    python vsl/outils/exporter.py            dossier autonome (double-clic sur index.html)
    python vsl/outils/exporter.py --unique   un seul fichier .html, à envoyer tel quel (ou zippé)

Destination : Téléchargements. À relancer après tout changement de voix ou de texte.

Le fichier unique embarque la page, la vidéo, les styles, le script de prise de RDV et la voix
(encodée dans le fichier). Seules les polices viennent d'internet ; sans connexion, le navigateur
prend ses polices par défaut. L'agenda Zeeg, lui, demande une connexion.
"""
import base64
import re
import shutil
import sys
import zipfile
from pathlib import Path

SITE = Path(__file__).resolve().parents[2]
SOURCE = SITE / "vsl" / "expert-comptable"
TELECHARGEMENTS = Path.home() / "Downloads"
NOM = "IZAIA-VSL-expert-comptable"

# Une balise fermante de script, même dans un bloc inerte, fermerait le bloc : on la maquille.
FERMANTE, MAQUILLEE = "</script", "<~/script"


def liens_absolus(page):
    # Hors du site, les liens internes pointent vers le site en ligne.
    return re.sub(r'href="/(?!/)', 'href="https://www.izaia.fr/', page)


def lire(chemin):
    return chemin.read_text(encoding="utf-8")


def remplacer(texte, ancien, nouveau):
    if texte.count(ancien) != 1:
        sys.exit(f"Repère introuvable ou en double : {ancien[:60]}")
    return texte.replace(ancien, nouveau)


def dossier():
    dest = TELECHARGEMENTS / NOM
    if dest.exists():
        shutil.rmtree(dest)
    (dest / "styles").mkdir(parents=True)
    for nom in ("lecteur.html", "voix.js", "voix.mp3"):
        shutil.copy2(SOURCE / nom, dest / nom)
    for nom in ("izaia-2026.css", "izaia-2026.js"):
        shutil.copy2(SITE / "styles" / nom, dest / "styles" / nom)
    page = liens_absolus(lire(SOURCE / "index.html").replace("../../styles/", "styles/"))
    (dest / "index.html").write_text(page, encoding="utf-8")
    return dest


def unique():
    # 1. Le lecteur, avec sa voix dans le fichier.
    mp3 = base64.b64encode((SOURCE / "voix.mp3").read_bytes()).decode("ascii")
    voix = remplacer(lire(SOURCE / "voix.js"), '"src": "voix.mp3"', f'"src": "data:audio/mpeg;base64,{mp3}"')
    lecteur = remplacer(lire(SOURCE / "lecteur.html"), '<script src="voix.js"></script>', f"<script>{voix}</script>")

    # 2. La page, avec ses styles et son script dans le fichier.
    page = liens_absolus(lire(SOURCE / "index.html"))
    page = remplacer(page, '<link rel="stylesheet" href="../../styles/izaia-2026.css">',
                     "<style>" + lire(SITE / "styles" / "izaia-2026.css") + "</style>")
    page = remplacer(page, '<script src="../../styles/izaia-2026.js"></script>',
                     "<script>" + lire(SITE / "styles" / "izaia-2026.js") + "</script>")

    # 3. Le lecteur voyage dans un bloc inerte ; la page le verse dans le cadre à l'ouverture.
    page = remplacer(page, ' src="lecteur.html?embed=1"', ' name="vsl-embed"')
    page = remplacer(
        page, "  function demander(){",
        f"  cadre.srcdoc=document.getElementById('lecteur-source').textContent.split('{MAQUILLEE}').join('{FERMANTE}');\n"
        "  function demander(){")
    bloc = '<script type="text/plain" id="lecteur-source">' + lecteur.replace(FERMANTE, MAQUILLEE) + "</script>\n"
    page = remplacer(page, "\n</main>\n", "\n</main>\n" + bloc)

    dest = TELECHARGEMENTS / f"{NOM}.html"
    dest.write_text(page, encoding="utf-8")
    # Beaucoup de messageries bloquent une pièce jointe .html ; le .zip passe.
    with zipfile.ZipFile(dest.with_suffix(".zip"), "w", zipfile.ZIP_DEFLATED) as z:
        z.write(dest, dest.name)
    return dest


def main():
    dest = unique() if "--unique" in sys.argv else dossier()
    fichiers = [dest, dest.with_suffix(".zip")] if dest.is_file() else sorted(x for x in dest.rglob("*") if x.is_file())
    print(dest.parent)
    for f in fichiers:
        print(f"  {f.name}  {f.stat().st_size // 1024} Ko")


if __name__ == "__main__":
    main()
