#!/usr/bin/env python3
"""Verifie qu'une page de verticale respecte les invariants du spec 2026-08-26.

Usage: python tools/check-page.py chemin/vers/index.html
Sortie: 0 si la page passe, 1 sinon.
"""
import os
import re
import sys

MONTANTS_AUTORISES = {"2 500", "5 000", "5 300"}

SECTIONS_REQUISES = [
    ("Ce que vous devez savoir", "bloc GEO"),
    ("n'enseigne pas", "bloc des negations"),
    ("Le prix, en clair", "bloc tarif"),
    ("Nous travaillons aussi avec", "maillage lateral"),
]

SIGNAUX = [
    "conforme", "conformes", "automatique", "automatiques", "complet", "complete",
    "revolution", "incontournable", "booster", "majeur", "considerable",
    "significativement", "leader", "innovant", "puissant",
]

CSS_INTERDITS = ["common.css", "refonte.css"]


def sans_accents(s):
    remp = {"à": "a", "â": "a", "é": "e", "è": "e", "ê": "e",
            "ë": "e", "î": "i", "ï": "i", "ô": "o", "ù": "u",
            "û": "u", "ü": "u", "ç": "c", "œ": "oe"}
    for k, v in remp.items():
        s = s.replace(k, v)
    return s


def texte_visible(html):
    html = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    txt = re.sub(r"<[^>]+>", " ", html)
    txt = txt.replace("&nbsp;", " ").replace("&amp;", "&")
    txt = txt.replace("&#39;", "'").replace("&rsquo;", "'").replace("&eacute;", "e")
    return re.sub(r"\s+", " ", txt)


def charger_noms_interdits():
    chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "noms-interdits.txt")
    if not os.path.exists(chemin):
        return None
    with open(chemin, encoding="utf-8") as fh:
        return [l.strip() for l in fh if l.strip() and not l.startswith("#")]


def verifier(chemin):
    with open(chemin, encoding="utf-8") as fh:
        html = fh.read()
    txt = texte_visible(html)
    bas = sans_accents(txt.lower())
    fails, warns = [], []

    if "!" in txt:
        fails.append(("EXCL", "point d'exclamation dans le texte visible"))

    # La graphie se controle sur le texte affiche et les metadonnees, jamais sur
    # les URL : un slug de lien externe n'est pas de la copie editoriale.
    html_sans_urls = re.sub(r'\s(?:href|src)="[^"]*"', " ", html)
    # Regle maison : aucun tiret cadratin dans la copie editoriale.
    # La puce de liste (.klist li::before) vit dans le CSS, hors du texte visible.
    n_cad = txt.count("—")
    if n_cad:
        fails.append(("CADRATIN", "%d tiret(s) cadratin dans le texte visible" % n_cad))

    for graphie in ["IzaIA", "IAZIA", "Izaia"]:
        if graphie in html_sans_urls:
            fails.append(("GRAPHIE", "graphie %s trouvee, ecrire IZAIA" % graphie))

    for montant in set(re.findall(r"\d\s?\d{3}(?=\s?€)", txt)):
        normalise = re.sub(r"\s+", " ", montant)
        if " " not in normalise:
            normalise = normalise[0] + " " + normalise[1:]
        if normalise not in MONTANTS_AUTORISES:
            fails.append(("MONTANT", "montant hors grille canonique : %s EUR" % normalise))

    if "QUA24120006" not in txt:
        fails.append(("QUALIOPI", "numero Qualiopi absent"))
    if "FORM'RH" not in txt and "FORM’RH" not in txt:
        fails.append(("QUALIOPI", "mention FORM'RH absente"))

    mentionne_aiact = "ai act" in bas or "reglement europeen sur l'intelligence" in bas
    if mentionne_aiact and "2 fevrier 2025" not in bas:
        fails.append(("AIACT", "AI Act mentionne sans la date du 2 fevrier 2025"))

    positions = {}
    for marqueur, libelle in SECTIONS_REQUISES:
        idx = txt.find(marqueur)
        if idx < 0:
            fails.append(("SECTION", "section absente : %s" % libelle))
        else:
            positions[marqueur] = idx

    if "Ce que vous devez savoir" in positions and "Le prix, en clair" in positions:
        if positions["Ce que vous devez savoir"] > positions["Le prix, en clair"]:
            fails.append(("ORDRE", "le bloc GEO doit preceder le bloc tarif"))

    idx_neg = txt.find("n'enseigne pas")
    if idx_neg >= 0:
        fin = positions.get("Le prix, en clair", idx_neg + 4000)
        if fin < idx_neg:
            fin = idx_neg + 4000
        section = txt[idx_neg:fin]
        n = len(re.findall(r"\bAucun", section))
        if n < 4:
            fails.append(("NEGATIONS", "%d negation(s) dans le bloc, quatre au minimum" % n))

    for css in CSS_INTERDITS:
        if css in html:
            fails.append(("CSS", "feuille d'ancienne generation liee : %s" % css))

    noms = charger_noms_interdits()
    if noms is None:
        warns.append(("NOM", "tools/noms-interdits.txt absent, controle des noms non effectue"))
    else:
        for nom in noms:
            if re.search(r"\b%s\b" % re.escape(nom), html, re.I):
                fails.append(("NOM", "nom propre interdit : %s" % nom))

    for signal in SIGNAUX:
        for m in re.finditer(r"\b%s\b" % signal, bas):
            debut = max(0, m.start() - 60)
            warns.append(("SIGNAL", "%s -> ...%s..." % (signal, txt[debut:m.end() + 40].strip())))

    return fails, warns


def main():
    # Les extraits cites peuvent contenir des caracteres absents de la console
    # Windows par defaut. On ne veut pas qu'un emoji fasse planter le controle.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    if len(sys.argv) != 2:
        print("usage: check-page.py <chemin/index.html>")
        return 2
    fails, warns = verifier(sys.argv[1])
    for code, msg in fails:
        print("FAIL %s - %s" % (code, msg))
    for code, msg in warns:
        print("WARN %s - %s" % (code, msg))
    print("--- %d echec(s), %d signal(aux) a relire" % (len(fails), len(warns)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
