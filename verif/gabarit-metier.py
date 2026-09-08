# -*- coding: utf-8 -*-
"""Remonte /notaire/ et /medecin/ sur le gabarit des onze pages metier.

Ces deux pages chargeaient encore common.css + refonte.css : la charte avait
bien ete migree, mais la structure restait celle de l'ancienne generation.
Elles partageaient 30 % de leurs classes avec /avocat/, la ou /cgp/ en partage
100 %.

Le script ne reecrit aucun texte. Il transporte le contenu existant dans les
coquilles 2026 (page-hero, section-pad, sec-alt, prose, situ, conf) et refuse
d'agir sur une page dont il ne reconnait pas la structure d'origine.
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DONNEUR = 'cgp/index.html'
CIBLES = {
    'notaire': ('Notaires', 'Formation · Notariat'),
    'medecin': ('Médecins', 'Formation · Cabinet médical'),
}

# L'encadre « referent metier » s'appuie sur .finance-hi. La page donneuse la
# definit deja ; ces regles ne servent que si l'on change un jour de donneuse.
FINANCE_HI = """
/* ---- Encadre en relief ---- */
.finance-hi{background:var(--paper-soft);border-left:3px solid var(--gold);border-radius:0 var(--radius-s) var(--radius-s) 0;padding:20px 24px;margin:26px 0}
.finance-hi b{display:block;font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--pine);margin-bottom:8px}
.finance-hi p{margin:0;font-size:16px;color:var(--txt)}
"""


def nettoie(html):
    """Texte d'un titre : on enleve le balisage, on garde les mots."""
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html)).strip()


def lire_source(dossier):
    s = open(os.path.join(dossier, 'index.html'), encoding='utf-8').read()
    d = {}

    # ---- en-tete de page ----
    m = re.search(r'(?s)<section class="hero page-hero">(.*?)</section>', s)
    if not m:
        raise SystemExit('%s : pas de hero reconnaissable' % dossier)
    hero = m.group(1)
    d['badge'] = nettoie(re.search(r'(?s)<div class="hero-badge">(.*?)</div>', hero).group(1))
    h1 = re.search(r'(?s)<h1[^>]*>(.*?)</h1>', hero).group(1)
    em = re.search(r'(?s)<em>(.*?)</em>', h1)
    d['h1'] = nettoie(re.sub(r'(?s)<em>.*?</em>', '', h1)).rstrip('.')
    d['frag'] = nettoie(em.group(1)) if em else ''
    d['chapo'] = nettoie(re.search(r'(?s)<p class="hero-sub">(.*?)</p>', hero).group(1))

    # ---- « vous vous reconnaissez ? » ----
    m = re.search(r'(?s)<section class="section section-alt">(.*?)</section>', s)
    if not m:
        raise SystemExit('%s : pas de section de situations' % dossier)
    bloc = m.group(1)
    d['titre_situ'] = nettoie(re.search(r'(?s)<h2[^>]*>(.*?)</h2>', bloc).group(1))
    d['situations'] = [
        (nettoie(t), p.strip())
        for t, p in re.findall(r'(?s)<div class="card">\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>', bloc)
    ]
    if not d['situations']:
        raise SystemExit('%s : aucune carte de situation trouvee' % dossier)

    # ---- corps redactionnel ----
    m = re.search(r'(?s)<div class="article-content">(.*?)</div>\s*</div>\s*</section>', s)
    if not m:
        raise SystemExit('%s : pas de corps redactionnel' % dossier)
    d['corps'] = m.group(1)

    # ---- banniere finale ----
    m = re.search(r'(?s)<section class="cta-banner">(.*?)</section>', s)
    if not m:
        raise SystemExit('%s : pas de banniere finale' % dossier)
    ban = m.group(1)
    d['cta_h2'] = nettoie(re.search(r'(?s)<h2[^>]*>(.*?)</h2>', ban).group(1))
    d['cta_p'] = nettoie(re.search(r'(?s)<p>(.*?)</p>', ban).group(1))

    # ---- metadonnees a conserver ----
    d['titre'] = re.search(r'<title>(.*?)</title>', s).group(1)
    d['desc'] = re.search(r'<meta name="description" content="([^"]*)"', s).group(1)
    d['og_titre'] = re.search(r'<meta property="og:title" content="([^"]*)"', s).group(1)
    d['og_desc'] = re.search(r'<meta property="og:description" content="([^"]*)"', s).group(1)
    return d


def decoupe_corps(corps):
    """Coupe le corps redactionnel a chaque <h2> : une section 2026 par titre."""
    corps = re.sub(r'(?s)<span class="tag">.*?</span>', '', corps)
    morceaux = re.split(r'(?s)(<h2[^>]*>.*?</h2>)', corps)
    sections = []
    titre = None
    tampon = morceaux[0]
    for i in range(1, len(morceaux), 2):
        if titre is not None or tampon.strip():
            sections.append((titre, tampon))
        titre = nettoie(morceaux[i])
        tampon = morceaux[i + 1]
    sections.append((titre, tampon))
    return [(t, c) for t, c in sections if t or c.strip()]


def rend_contenu(html):
    """Reecrit le contenu d'une section : encadre converti, styles retires."""
    html = re.sub(
        r'(?s)<div class="info-box">\s*<strong>[^<]*?([A-ZÀ-Ý][^<:]*)</strong>\s*:?\s*(.*?)</div>',
        lambda m: '<div class="finance-hi"><b>%s</b><p>%s</p></div>'
                  % (m.group(1).strip(), m.group(2).strip()),
        html)
    html = re.sub(r'<(p|ul|li|h3)(?:\s[^>]*)?>', lambda m: '<%s>' % m.group(1), html)
    html = re.sub(r'\n\s*\n+', '\n', html)
    return '\n'.join('      ' + l.strip() for l in html.strip().split('\n') if l.strip())


def construis(dossier, libelle, kicker, tete, pied, style, qualiopi):
    d = lire_source(dossier)
    url = 'https://www.izaia.fr/%s/' % dossier

    # --- en-tete du document ---
    tete = re.sub(r'<title>.*?</title>', lambda m: '<title>%s</title>' % d['titre'], tete)
    tete = re.sub(r'<meta name="description" content="[^"]*"',
                  lambda m: '<meta name="description" content="%s"' % d['desc'], tete)
    tete = re.sub(r'<link rel="canonical" href="[^"]*"',
                  lambda m: '<link rel="canonical" href="%s"' % url, tete)
    for prop, val in (('og:title', d['og_titre']), ('og:description', d['og_desc']),
                      ('og:url', url), ('twitter:title', d['og_titre']),
                      ('twitter:description', d['og_desc'])):
        marque = 'property' if prop.startswith('og:') else 'name'
        tete = re.sub(r'<meta %s="%s" content="[^"]*"' % (marque, prop),
                      lambda m, k=marque, p=prop, v=val: '<meta %s="%s" content="%s"' % (k, p, v),
                      tete)

    # --- donnees structurees : on ne garde que ce que la page dit vraiment ---
    # Ni FAQ ni prix affiche sur ces deux pages : on ne les declare donc pas.
    tete = re.sub(r'(?s)<script type="application/ld\+json">\s*\{[^<]*?"@type": "FAQPage".*?</script>\s*',
                  '', tete)
    premiere_liste = re.search(r'(?s)<ul>(.*?)</ul>', d['corps'])
    enseigne = re.findall(r'<li><strong>([^<]+)</strong>',
                          premiere_liste.group(1) if premiere_liste else '')
    bloc_cours = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "%s",
  "description": "%s",
  "url": "%s",
  "inLanguage": "fr-FR",
  "provider": {
    "@type": "Organization",
    "name": "FORM'RH",
    "description": "Organisme de formation certifié Qualiopi, n° QUA24120006."
  },
  "teaches": [
%s
  ],
  "hasCourseInstance": {
    "@type": "CourseInstance",
    "courseMode": "onsite",
    "courseWorkload": "PT14H",
    "location": {
      "@type": "Place",
      "name": "Dans les locaux du cabinet, partout en France"
    }
  }
}
</script>''' % (d['h1'], d['chapo'], url, ',\n'.join('    "%s"' % t for t in enseigne))
    tete = re.sub(r'(?s)<script type="application/ld\+json">\s*\{[^<]*?"@type": "Course".*?</script>',
                  lambda m: bloc_cours, tete, count=1)
    tete = re.sub(r'"name": "Gestion de patrimoine"',
                  lambda m: '"name": "%s"' % libelle, tete)
    complement = '' if '.finance-hi' in style else FINANCE_HI
    tete = re.sub(r'(?s)<style>.*?</style>',
                  lambda m: '<style>%s%s</style>' % (style, complement), tete, count=1)

    # --- corps de page ---
    parts = ['''<nav class="fil-ariane container" aria-label="Fil d'Ariane">
  <ol>
    <li><a href="/">Accueil</a></li>
    <li><a href="/formation/">Formations</a></li>
    <li><span aria-current="page">%s</span></li>
  </ol>
</nav>

<!-- ================= HERO ================= -->
<section class="page-hero">
  <div class="container">
    <span class="kicker on-dark">%s</span>
    <h1>%s</h1>
    <p class="hero-frag">%s</p>
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
      <p class="first">%s</p>
      <p>IZAIA est une formation proposée par FORM'RH, organisme de formation certifié Qualiopi (n°&nbsp;QUA24120006). Nous intervenons dans vos locaux, partout en France, depuis Lyon.</p>
%s
    </div>
  </div>
</section>''' % (libelle, kicker, d['h1'], d['frag'], d['chapo'], qualiopi)]

    situ = '\n'.join(
        '      <div class="situ">\n        <b>%s</b>\n        <span>%s</span>\n      </div>' % (t, p)
        for t, p in d['situations'])
    parts.append('''<!-- ================= SITUATIONS ================= -->
<section class="section-pad sec-alt">
  <div class="container">
    <h2>%s</h2>
    <div class="situations prose">
%s
    </div>
  </div>
</section>''' % (d['titre_situ'], situ))

    alt = False
    for k, (titre, contenu) in enumerate(decoupe_corps(d['corps'])):
        ident = ' id="programme"' if k == 0 else ''
        if titre and 'tarif' in titre.lower():
            ident = ' id="tarif"'
        classe = 'section-pad sec-alt' if alt else 'section-pad'
        alt = not alt
        parts.append('''<!-- ================= %s ================= -->
<section class="%s"%s>
  <div class="container">
%s    <div class="prose">
%s
    </div>
  </div>
</section>''' % ((titre or 'SUITE').upper()[:44], classe, ident,
                 '    <h2>%s</h2>\n' % titre if titre else '',
                 rend_contenu(contenu)))

    parts.append('''<!-- ================= ET MAINTENANT ================= -->
<section class="section-pad conf">
  <div class="container">
    <span class="kicker on-dark">Et maintenant</span>
    <h2>%s</h2>
    <p>%s</p>
    <div class="hero-actions" style="margin-top:26px">
      <a class="btn btn-gold js-rdv" href="https://zeeg.me/izaia/Rdv-decouverte-Izaia?duration=30">RDV téléphonique sans engagement</a>
    </div>
  </div>
</section>''' % (d['cta_h2'], d['cta_p']))

    return tete + '\n\n'.join(parts) + '\n\n' + pied


def principal():
    src = open(DONNEUR, encoding='utf-8').read()
    i = src.find('<nav class="fil-ariane')
    j = src.rfind('<footer')
    if i < 0 or j < 0:
        raise SystemExit('%s : squelette introuvable' % DONNEUR)
    tete, pied = src[:i], src[j:]
    style = re.search(r'(?s)<style>(.*?)</style>', tete).group(1)
    qualiopi = re.search(r'(?s)([ \t]*<img class="qualiopi-mini".*?</p>)', src).group(1)

    for dossier, (libelle, kicker) in CIBLES.items():
        html = construis(dossier, libelle, kicker, tete, pied, style, qualiopi)
        open(os.path.join(dossier, 'index.html'), 'w', encoding='utf-8', newline='\n').write(html)
        print('  %s/index.html reconstruit : %d octets' % (dossier, len(html)))


if __name__ == '__main__':
    principal()
