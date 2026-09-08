# -*- coding: utf-8 -*-
"""Verifie qu'aucune ancre ne pointe vers un identifiant absent de sa page.

Le pied de page a ete transplante depuis l'accueil sur tout le site, mais
ses ancres etaient restees nues : sur /avocat/, « href="#integrer" »
cherchait un id="integrer" qui n'existe que sur l'accueil. Neuf liens morts
par sous-page, trente-sept sous-pages. L'en-tete, lui, ecrivait deja
« /#integrer » et fonctionnait.

Une ancre nue reste legitime quand la cible est sur la meme page : les
pages metier ont un « href="#programme" » et un id="programme".
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

EXCLUS = ('mockups', 'realisations', 'sante', '.git', 'node_modules')


def pages():
    for racine, _, fichiers in os.walk('.'):
        if any(x in racine for x in EXCLUS):
            continue
        for f in sorted(fichiers):
            if f.endswith('.html'):
                yield os.path.join(racine, f)


def identifiants_accueil():
    """Les sections de l'accueil, cible legitime d'une ancre « /#x »."""
    s = re.sub(r'(?s)<!--.*?-->', '', open('index.html', encoding='utf-8').read())
    return set(re.findall(r'id="([^"]+)"', s))


ACCUEIL = identifiants_accueil()


def principal():
    fautives = []
    examinees = 0
    for p in pages():
        s = open(p, encoding='utf-8').read()
        s = re.sub(r'(?s)<!--.*?-->', '', s)
        examinees += 1
        identifiants = set(re.findall(r'id="([^"]+)"', s))
        # Ancre sur la page courante : la cible doit exister ici.
        mortes = {a for a in re.findall(r'href="#([a-zA-Z][\w-]*)"', s)
                  if a not in identifiants}
        # Ancre vers l'accueil, ecrite « /#x » ou « ../#x » : la cible doit
        # exister sur l'accueil. Les pages villes visaient /#programme et
        # /#tarif, deux sections qui n'ont jamais existe la-bas.
        mortes |= {a for a in re.findall(r'href="(?:/|\.\./)#([a-zA-Z][\w-]*)"', s)
                   if a not in ACCUEIL}
        mortes = sorted(mortes)
        if mortes:
            fautives.append((p.replace(chr(92), '/')[2:], mortes))

    if fautives:
        for chemin, mortes in fautives:
            print('  [KO] %-46s %s' % (chemin, ', '.join(mortes)))
        print('  %d page(s) sur %d portent une ancre qui ne mene nulle part'
              % (len(fautives), examinees))
        return 1

    print('  [OK] les %d pages examinees : aucune ancre vers un identifiant absent'
          % examinees)
    return 0


if __name__ == '__main__':
    sys.exit(principal())
