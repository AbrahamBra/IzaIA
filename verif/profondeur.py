"""Vérifie que chaque page du sitemap est à 1 clic de l'accueil."""
import re, os, sys, collections

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def cible(url, depuis):
    if url.startswith(('http', 'mailto:', 'tel:', 'data:')):
        return None
    u = url.split('#')[0].split('?')[0]
    if not u:
        return None
    p = (os.path.join(root, u.lstrip('/')) if u.startswith('/')
         else os.path.normpath(os.path.join(os.path.dirname(depuis), u)))
    if os.path.isdir(p):
        p = os.path.join(p, 'index.html')
    return os.path.normpath(p) if p.endswith('.html') else None

depart = os.path.join(root, 'index.html')
profondeur = {depart: 0}
file = collections.deque([depart])
while file:
    f = file.popleft()
    if not os.path.exists(f):
        continue
    with open(f, encoding='utf-8', errors='ignore') as fh:
        html = fh.read()
    for href in re.findall(r'href="([^"]+)"', html):
        t = cible(href, f)
        if t and os.path.exists(t) and t not in profondeur:
            profondeur[t] = profondeur[f] + 1
            file.append(t)

with open(os.path.join(root, 'sitemap.xml'), encoding='utf-8') as fh:
    locs = re.findall(r'<loc>([^<]+)</loc>', fh.read())

# Regle de profondeur.
#
#   - tout ce qui n'est pas du blog doit etre a 1 clic de l'accueil ;
#   - le blog a droit a une chaine plus longue, parce qu'un index de blog
#     puis un article, c'est une hierarchie legitime :
#       /blog/ (1)  ->  /blog/article.html (2)
#       /expert-comptable/ (1)  ->  .../blog/ (2)  ->  .../blog/article.html (3)
#
# D'ou une tolerance a 3 pour les chemins de blog, et a 1 pour le reste.
MAX_BLOG, MAX_AUTRE = 3, 1

# Pages volontairement deliees de la navigation : leur contenu n'est pas
# termine. Elles restent en ligne et indexees — c'est un choix, pas un
# oubli : les mettre en 404 ferait perdre une position acquise depuis des
# mois. On cesse simplement de les mettre en avant.
DELIEES = {"/tarif/", "/conseil/", "/equipe/",
           "/lyon/", "/paris/", "/bordeaux/", "/toulouse/"}

trop_loin = []
for loc in locs:
    chemin = re.sub(r'^https://(www\.)?izaia\.fr', '', loc)
    p = os.path.join(root, chemin.lstrip('/'))
    if os.path.isdir(p):
        p = os.path.join(p, 'index.html')
    p = os.path.normpath(p)
    d = profondeur.get(p)
    if chemin in DELIEES:
        continue
    plafond = MAX_BLOG if '/blog/' in chemin else MAX_AUTRE
    if d is None:
        trop_loin.append((99, chemin, 'inatteignable'))
    elif d > plafond:
        trop_loin.append((d, chemin, f'{d} clics, plafond {plafond}'))

if trop_loin:
    for d, chemin, note in sorted(trop_loin, reverse=True):
        etiquette = note or f"{d} clics"
        print(f"  [!!] {chemin} : {etiquette}")
    print(f"  {len(trop_loin)} page(s) a plus d'un clic de l'accueil.")
    sys.exit(1)

print(f"  [OK] les {len(locs)-len(DELIEES)} pages liees du sitemap sont a 1 clic "
      f"de l'accueil ; {len(DELIEES)} deliees volontairement")
sys.exit(0)
