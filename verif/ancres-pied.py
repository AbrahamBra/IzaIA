# -*- coding: utf-8 -*-
"""Prefixe les ancres du pied de page pour qu'elles pointent vers l'accueil.

Le pied de page a ete transplante depuis l'accueil sur toutes les pages du
site. Ses ancres sont restees nues : sur /avocat/, « href="#integrer" »
cherche un id="integrer" qui n'existe que sur l'accueil. Les neuf liens du
pied de page ne menaient donc nulle part sur les trente-sept sous-pages.
L'en-tete, lui, etait deja correct : il utilise « /#integrer ».

On prefixe aussi sur l'accueil, ou « /#integrer » se comporte exactement
comme « #integrer » : sans cela le pied de page divergerait entre l'accueil
et le reste, et l'assertion [A8] qui compare les deux jeux de liens
tomberait.
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
        for f in fichiers:
            if f.endswith('.html'):
                yield os.path.join(racine, f)


def principal():
    total_liens = 0
    total_pages = 0
    for p in sorted(pages()):
        s = open(p, encoding='utf-8').read()
        m = re.search(r'(?s)(<footer[^>]*>.*?</footer>)', s)
        if not m:
            continue
        pied = m.group(1)
        nus = re.findall(r'href="#([a-z-]+)"', pied)
        if not nus:
            continue
        corrige = re.sub(r'href="#([a-z-]+)"', lambda x: 'href="/#%s"' % x.group(1), pied)
        s = s[:m.start(1)] + corrige + s[m.end(1):]
        open(p, 'w', encoding='utf-8').write(s)
        total_pages += 1
        total_liens += len(nus)
        print('  %-52s %d ancre(s)' % (p.replace(chr(92), '/')[2:], len(nus)))
    print('\n  %d page(s), %d ancre(s) prefixee(s)' % (total_pages, total_liens))


if __name__ == '__main__':
    principal()
