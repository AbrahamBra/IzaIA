# -*- coding: utf-8 -*-
"""Genere la section des exemples d'une page agents et la greffe dans son corps."""
import io
import os

import demos as demonstrations

ICI = os.path.dirname(os.path.abspath(__file__))
NOMBRES = {15: "Quinze", 16: "Seize", 17: "Dix-sept"}
DEBUT = "<!-- ================= CAS D'USAGE ================= -->"
# Les exemples passent avant « ce qu'il faut savoir » : c'est ce que le visiteur vient chercher.
FIN = "<!-- ================= CE QU'IL FAUT SAVOIR ================= -->"


def greffer(corps, familles, titre, intro, etiquettes, prerequis, demos=None):
    """familles : [(ancre, titre, [(nom, avant, outil, humain[, a_savoir])])].
    titre contient un %s, remplace par le nombre d'exemples en toutes lettres.

    Regle d'ecriture des cartes (relecture du 2026-10-01) : l'etiquette d'une
    case est le sujet de sa phrase. La case de l'outil ne parle que de l'outil,
    y compris pour dire ce qu'il ne fait pas. La case de la personne ne parle
    que de la personne, et commence par « Il ». Toute remarque qui ne releve ni
    de l'un ni de l'autre (ce que fait deja un logiciel, une condition d'acces)
    va dans la ligne facultative « A savoir ».

    prerequis : {titre de l'exemple: ce qu'il faut pour demarrer}. Une ligne
    par carte, obligatoire : ce que le client doit fournir ou ouvrir (un
    acces, des modeles, des documents) avant que l'agent IA puisse travailler.

    demos : {titre de l'exemple: nom de la demonstration animee}, facultatif.
    La demonstration se place sous le titre de la carte, avant le texte."""
    demos = demos or {}
    assert set(demos) <= set(e[0] for f in familles for e in f[2]), "demonstration sans carte"
    total = sum(len(f[2]) for f in familles)
    titres = [e[0] for f in familles for e in f[2]]
    assert sorted(titres) == sorted(prerequis), (
        "prerequis manquant ou en trop : %s" % (set(titres) ^ set(prerequis)))
    mot = NOMBRES[total]
    l = []
    l.append(DEBUT)
    l.append('<section class="section-pad" id="cas">')
    l.append('  <div class="container">')
    l.append('    <div class="section-head">')
    l.append('      <span class="kicker">Les exemples</span>')
    l.append("      <h2>%s</h2>" % (titre % mot))
    l.append("      <p>%s</p>" % intro)
    if demos:
        # La conclusion des videos est commune : ecrite une fois ici, et non seize
        # fois dans les transcriptions. Le lecteur la reprend pour le sous-titre.
        l.append('      <p class="demo-conclusion">Chaque vidéo se termine par la même conclusion : '
                 '« <span id="demo-fin">%s</span> »</p>' % demonstrations.FIN)
    l.append('    </div>')
    # Sans script, chaque pastille est un lien vers sa famille. Le script de page
    # les transforme en filtres.
    l.append('    <div class="filtres" aria-label="Filtrer les exemples par famille">')
    l.append('      <a href="#cas" data-filtre="tous" aria-pressed="true">Tous <span>%d</span></a>' % total)
    for ancre, nom_famille, exemples in familles:
        l.append('      <a href="#%s" data-filtre="%s">%s <span>%d</span></a>'
                 % (ancre, ancre, nom_famille, len(exemples)))
    l.append('    </div>')
    numero = 0
    for ancre, nom_famille, exemples in familles:
        l.append('    <div class="famille-bloc" data-famille="%s">' % ancre)
        l.append('      <h3 class="famille" id="%s">%s</h3>' % (ancre, nom_famille))
        l.append('      <div class="exemples">')
        for exemple in exemples:
            nom, avant, outil, humain = exemple[:4]
            a_savoir = exemple[4] if len(exemple) > 4 else None
            assert humain.startswith("Il "), "case de la personne sans « Il » : %s" % nom
            assert outil.startswith(("Il ", "À partir")), "case de l'outil sans « Il » : %s" % nom
            numero += 1
            # Ouvert par defaut : tout le texte est lisible sans script. Le script
            # de page ne replie les cartes que sur telephone.
            l.append('        <details class="exemple" open>')
            l.append('          <summary><span class="num" aria-hidden="true">%02d</span><h4>%s</h4></summary>'
                     % (numero, nom))
            if nom in demos:
                l.append("          " + demonstrations.bloc(demos[nom]).replace("\n", "\n          "))
            l.append('          <dl class="cas">')
            for etiquette, texte in zip(etiquettes, (avant, outil, humain)):
                l.append("            <div><dt>%s</dt><dd>%s</dd></div>" % (etiquette, texte))
            l.append('            <div class="prerequis"><dt>Prérequis</dt><dd>%s</dd></div>' % prerequis[nom])
            if a_savoir:
                l.append('            <div class="savoir"><dt>À savoir</dt><dd>%s</dd></div>' % a_savoir)
            l.append('          </dl>')
            l.append('        </details>')
        l.append('      </div>')
        l.append('    </div>')
    l.append('  </div>')
    l.append('</section>')
    section = "\n".join(l) + "\n\n"

    chemin = os.path.join(ICI, corps)
    with io.open(chemin, encoding="utf-8") as fh:
        s = fh.read()
    s = s[:s.index(DEBUT)] + section + s[s.index(FIN):]
    bouton = "Voir les %s exemples</a>" % mot.lower()
    assert bouton in s, "le bouton du bandeau n'annonce pas %s exemples" % mot.lower()
    with io.open(chemin, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(s)
    print(total, "exemples ecrits dans", corps)
