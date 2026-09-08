# -*- coding: utf-8 -*-
"""Aligne le libelle des liens sur ce que leur destination contient reellement.

/tarif/ et /programme/ ont ete supprimees, et les liens qui y menaient ont
ete repointes vers /formation/. Restaient des libelles qui promettaient une
page de tarifs ou un programme detaille : un bouton « Voir les tarifs » qui
ouvre la liste des formations est un piege, meme si le lien fonctionne.

Deux traitements selon la nature du lien :

  - les appels a l'action et les renvois navigationnels sont renommes ; les
    onze pages metier affichent chacune leur programme et leur prix, donc
    « les formations et leurs tarifs » est exact ;

  - les renvois descriptifs au « Jour 1 » ne designent aucune page. On garde
    la phrase et on deplace le lien sur « la formation », qui est bien ce
    que /formation/ presente.

Le script refuse d'agir si une tournure attendue a change.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REMPLACEMENTS = [
    # --- appels a l'action ---
    ('charte-ia/index.html',
     '<a href="/formation/" class="btn btn-secondary">Voir le programme</a>',
     '<a href="/formation/" class="btn btn-secondary">Voir les formations par métier</a>'),
    ('chatgpt-formation/index.html',
     '<a href="/formation/" class="btn btn-secondary">Voir le programme</a>',
     '<a href="/formation/" class="btn btn-secondary">Voir les formations par métier</a>'),
    ('copilot-formation/index.html',
     '<a href="/formation/" class="btn btn-secondary">Voir le programme</a>',
     '<a href="/formation/" class="btn btn-secondary">Voir les formations par métier</a>'),
    ('faq/index.html',
     '<a href="/formation/" class="btn btn-secondary">Voir le programme</a>',
     '<a href="/formation/" class="btn btn-secondary">Voir les formations par métier</a>'),
    ('methode-actif/index.html',
     '<a href="/formation/" class="btn btn-secondary">Voir le programme</a>',
     '<a href="/formation/" class="btn btn-secondary">Voir les formations par métier</a>'),
    ('rgpd-ia/index.html',
     '<a href="/formation/" class="btn btn-secondary">Voir le programme</a>',
     '<a href="/formation/" class="btn btn-secondary">Voir les formations par métier</a>'),
    ('financement-opco-ia/index.html',
     '<a href="/formation/" class="btn btn-secondary">Voir les tarifs</a>',
     '<a href="/formation/" class="btn btn-secondary">Voir les formations et leurs tarifs</a>'),

    # --- renvois dans le texte ---
    ('chatgpt-formation/index.html',
     'Voir <a href="/formation/">le programme complet</a>.',
     'Voir <a href="/formation/">le programme de votre métier</a>.'),
    ('faq/index.html',
     'Voir <a href="/formation/" style="color:var(--accent);">le programme complet</a>.',
     'Voir <a href="/formation/" style="color:var(--accent);">le programme de votre métier</a>.'),
    ('chatgpt-formation/index.html',
     '<a href="/formation/">Voir tous les tarifs</a>.',
     '<a href="/formation/">Voir les formations et leurs tarifs</a>.'),
    ('copilot-formation/index.html',
     '<a href="/formation/">Voir tous les tarifs</a>.',
     '<a href="/formation/">Voir les formations et leurs tarifs</a>.'),
    ('faq/index.html',
     'Voir <a href="/formation/" style="color:var(--accent);">les tarifs détaillés</a>.',
     'Voir <a href="/formation/" style="color:var(--accent);">les formations et leurs tarifs</a>.'),
    ('financement-opco-ia/index.html',
     '<li><a href="/formation/">Tous les tarifs IzaIA et formats de financement</a></li>',
     '<li><a href="/formation/">Les formations IzaIA et leurs tarifs</a></li>'),
    ('methode-actif/index.html',
     '<li><a href="/formation/">Le programme détaillé de la formation IA</a></li>',
     '<li><a href="/formation/">Les formations IzaIA, métier par métier</a></li>'),

    # --- renvois descriptifs : le lien se deplace sur « la formation » ---
    ('charte-ia/index.html',
     'du <a href="/formation/">Jour 1 de la formation</a>, qui pose',
     'du Jour 1 de <a href="/formation/">la formation</a>, qui pose'),
    ('methode-actif/index.html',
     'principaux du <a href="/formation/">Jour 1</a>.',
     'principaux du Jour 1 de <a href="/formation/">la formation</a>.'),
    ('rgpd-ia/index.html',
     'le contenu du <a href="/formation/">Jour 1 de la formation IzaIA</a>.',
     'le contenu du Jour 1 de <a href="/formation/">la formation IzaIA</a>.'),
]


def principal():
    manquants = []
    for fichier, avant, _ in REMPLACEMENTS:
        if open(fichier, encoding='utf-8').read().count(avant) != 1:
            manquants.append((fichier, avant))
    if manquants:
        print('  Tournures introuvables ou ambigues, aucune modification :')
        for fichier, avant in manquants:
            print('    %-34s %s' % (fichier, avant[:70]))
        return 1

    par_fichier = {}
    for fichier, avant, apres in REMPLACEMENTS:
        par_fichier.setdefault(fichier, []).append((avant, apres))
    for fichier, paires in sorted(par_fichier.items()):
        s = open(fichier, encoding='utf-8').read()
        for avant, apres in paires:
            s = s.replace(avant, apres, 1)
        open(fichier, 'w', encoding='utf-8').write(s)
        print('  %-38s %d libelle(s)' % (fichier, len(paires)))
    print('\n  %d libelle(s) corrige(s) sur %d fichier(s)'
          % (len(REMPLACEMENTS), len(par_fichier)))
    return 0


if __name__ == '__main__':
    sys.exit(principal())
