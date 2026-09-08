# -*- coding: utf-8 -*-
"""Fusionne /lyon/, /paris/, /bordeaux/ et /toulouse/ en une page unique.

Les quatre pages partageaient 35 a 37 % de leur texte deux a deux, pour
430 a 470 mots chacune : meme squelette, nom de ville substitue, et un
paragraphe de couleur locale. C'est le schema que Google appelle « doorway
page », et il est sanctionne comme motif, pas seulement ignore.

Une seule des quatre reposait sur un fait verifiable : NGM-Immersion est
reellement etabli 12 rue de la Part-Dieu a Lyon. Ce fait est conserve ; les
descriptions economiques de Paris, Bordeaux et Toulouse, qui n'engagent
rien et ne se verifient pas, ne le sont pas.

Aucune phrase n'est inventee : tout le texte de la page produite provient
des quatre pages sources ou de llms.txt, qui porte deja la formulation
validee sur le perimetre d'intervention.

La page reste deliee et hors sitemap : elle attend la relecture du client,
comme les autres pages non relues.
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DONNEUR = 'cgp/index.html'
CIBLE = 'presentiel'
VILLES = ('lyon', 'paris', 'bordeaux', 'toulouse')

TITRE = "Formation IA en présentiel, partout en France | IzaIA"
DESCRIPTION = ("Formation IA de 2 jours en présentiel, dans vos locaux, partout en France. "
               "RGPD, méthode ACTIF, automatisations Make ou n8n. Jusqu'à 10 participants. "
               "Financement OPCO et FAF possible.")


def verifie_sources():
    """Refuse d'agir si une phrase reprise n'est plus dans les sources."""
    attendues = [
        ('lyon', "12 rue de la Part-Dieu, 69003 Lyon"),
        ('lyon', "RGPD, charte IA feux tricolores, méthode ACTIF, anonymisation, "
                 "première base de connaissance."),
        ('lyon', "Classification emails Gmail/Outlook, brouillons assistés, "
                 "base de connaissance, 3 workflows Make ou n8n."),
        ('lyon', "Financement <strong>OPCO Atlas</strong>"),
    ]
    manquantes = []
    for ville, phrase in attendues:
        chemin = os.path.join(ville, 'index.html')
        if not os.path.exists(chemin) or phrase not in open(chemin, encoding='utf-8').read():
            manquantes.append((ville, phrase))
    return manquantes


CORPS = '''<nav class="fil-ariane container" aria-label="Fil d'Ariane">
  <ol>
    <li><a href="/">Accueil</a></li>
    <li><a href="/formation/">Formations</a></li>
    <li><span aria-current="page">En présentiel</span></li>
  </ol>
</nav>

<!-- ================= HERO ================= -->
<section class="page-hero">
  <div class="container">
    <span class="kicker on-dark">Formation · Présentiel</span>
    <h1>Formation IA en présentiel, partout en France</h1>
    <p class="hero-frag">Deux jours dans vos locaux. Dix participants au maximum.</p>
    <div class="hero-actions">
      <a class="btn btn-gold js-rdv" href="https://zeeg.me/izaia/Rdv-decouverte-Izaia?duration=30">RDV téléphonique sans engagement</a>
      <a class="btn btn-ghost on-dark" href="#programme">Voir le programme</a>
    </div>
  </div>
</section>

<!-- ================= PROPOS LIMINAIRE ================= -->
<section class="section-pad">
  <div class="container">
    <div class="prose">
      <p class="first">La formation se déroule chez vous, dans vos locaux, sur un ou deux jours selon le format. Nous nous déplaçons : c'est à nous de venir, pas à vos équipes de se libérer une journée de transport en plus d'une journée de formation.</p>
      <p>IZAIA est édité par NGM-Immersion, établi 12&nbsp;rue de la Part-Dieu, 69003&nbsp;Lyon. Nous intervenons en présentiel dans toute la France, notamment à Paris, Lyon, Bordeaux et Toulouse.</p>
      <p>IZAIA est une formation proposée par FORM'RH, organisme de formation certifié Qualiopi (n°&nbsp;QUA24120006).</p>
__QUALIOPI__
    </div>
  </div>
</section>

<!-- ================= DEROULE ================= -->
<section class="section-pad sec-alt" id="programme">
  <div class="container">
    <h2>Deux journées, chez vous</h2>
    <div class="situations prose">
      <div class="situ">
        <b>Jour 1 &middot; Fondamentaux et conformité</b>
        <span>RGPD, charte IA feux tricolores, méthode ACTIF, anonymisation, première base de connaissance. 9h00 – 17h30.</span>
      </div>
      <div class="situ">
        <b>Jour 2 &middot; Automatisations</b>
        <span>Classification des emails Gmail ou Outlook, brouillons assistés, base de connaissance, trois workflows Make ou n8n. 9h00 – 17h30.</span>
      </div>
    </div>
  </div>
</section>

<!-- ================= PAR METIER ================= -->
<section class="section-pad">
  <div class="container">
    <h2>Le contenu s'adapte à votre métier</h2>
    <div class="prose">
      <p>Le déroulé ci-dessus est le socle commun. Les ateliers, les exemples et les cas travaillés changent selon la profession : ce qu'on montre à un cabinet d'avocats n'est pas ce qu'on montre à un EHPAD ou à un site industriel.</p>
      <p><a href="/formation/">Voir les onze formations par métier</a>, chacune avec son programme et son prix.</p>
    </div>
  </div>
</section>

<!-- ================= FINANCEMENT ================= -->
<section class="section-pad sec-alt" id="financement">
  <div class="container">
    <h2>Financement</h2>
    <div class="prose">
      <p>Le tarif est le même partout en France : il ne dépend pas de la ville, mais du format retenu et de l'effectif, pour toute l'équipe et jusqu'à dix participants.</p>
      <p>Un financement OPCO Atlas, FAF ou par un autre dispositif est possible selon votre statut. <a href="/formation/">Chaque formation affiche son prix</a>.</p>
    </div>
  </div>
</section>

<!-- ================= ET MAINTENANT ================= -->
<section class="section-pad conf">
  <div class="container">
    <span class="kicker on-dark">Et maintenant</span>
    <h2>Prêt à former votre équipe ?</h2>
    <p>Nous intervenons partout en France. Devis sous 24 h ouvrées, sans engagement.</p>
    <div class="hero-actions" style="margin-top:26px">
      <a class="btn btn-gold js-rdv" href="https://zeeg.me/izaia/Rdv-decouverte-Izaia?duration=30">RDV téléphonique sans engagement</a>
    </div>
  </div>
</section>'''


def construis():
    src = open(DONNEUR, encoding='utf-8').read()
    i = src.find('<nav class="fil-ariane')
    j = src.rfind('<footer')
    tete, pied = src[:i], src[j:]
    qualiopi = re.search(r'(?s)([ \t]*<img class="qualiopi-mini".*?</p>)', src).group(1)
    url = 'https://www.izaia.fr/%s/' % CIBLE

    tete = re.sub(r'<title>.*?</title>', lambda m: '<title>%s</title>' % TITRE, tete)
    tete = re.sub(r'<meta name="description" content="[^"]*"',
                  lambda m: '<meta name="description" content="%s"' % DESCRIPTION, tete)
    tete = re.sub(r'<link rel="canonical" href="[^"]*"',
                  lambda m: '<link rel="canonical" href="%s"' % url, tete)
    for marque, prop, val in (
            ('property', 'og:title', TITRE), ('property', 'og:description', DESCRIPTION),
            ('property', 'og:url', url),
            ('name', 'twitter:title', TITRE), ('name', 'twitter:description', DESCRIPTION)):
        tete = re.sub(r'<meta %s="%s" content="[^"]*"' % (marque, prop),
                      lambda m, k=marque, p=prop, v=val: '<meta %s="%s" content="%s"' % (k, p, v),
                      tete)
    # Ni FAQ ni prix affiche sur cette page : on ne declare que le fil d'Ariane.
    tete = re.sub(r'(?s)<script type="application/ld\+json">\s*\{[^<]*?"@type": "FAQPage".*?</script>\s*',
                  '', tete)
    tete = re.sub(r'(?s)<script type="application/ld\+json">\s*\{[^<]*?"@type": "Course".*?</script>\s*',
                  '', tete)
    tete = re.sub(r'"name": "Gestion de patrimoine"',
                  lambda m: '"name": "En présentiel"', tete)

    corps = CORPS.replace('__QUALIOPI__', qualiopi)
    os.makedirs(CIBLE, exist_ok=True)
    chemin = os.path.join(CIBLE, 'index.html')
    open(chemin, 'w', encoding='utf-8', newline='\n').write(tete + corps + '\n\n' + pied)
    return chemin


def principal():
    manquantes = verifie_sources()
    if manquantes:
        print('  Sources modifiees, aucune fusion :')
        for ville, phrase in manquantes:
            print('    %-12s %s' % (ville, phrase[:70]))
        return 1
    chemin = construis()
    print('  %s cree : %d octets' % (chemin, os.path.getsize(chemin)))
    print('  les quatre pages villes peuvent maintenant etre supprimees et redirigees')
    return 0


if __name__ == '__main__':
    sys.exit(principal())
