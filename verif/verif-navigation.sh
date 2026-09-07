#!/usr/bin/env bash
# Harnais de vérification du chantier « plomberie de navigation ».
#   bash verif/verif-navigation.sh          → vérifie les fichiers locaux
#   bash verif/verif-navigation.sh --prod   → vérifie aussi https://www.izaia.fr
set -uo pipefail
cd "$(dirname "$0")/.."

ROUGE=$'\033[31m'; VERT=$'\033[32m'; GRIS=$'\033[90m'; ZERO=$'\033[0m'
# Note : on ecrit « || true » et jamais « || echo 0 ». grep -c affiche deja
# « 0 » quand il ne trouve rien, tout en sortant en erreur : « || echo 0 »
# ajouterait un second zero et casserait le test d'entier — et seulement le
# jour ou le compte tombe a zero, c'est-a-dire quand l'assertion devrait passer.
ECHECS=0
ok()  { printf "  %s✓%s %s\n" "$VERT" "$ZERO" "$1"; }
ko()  { printf "  %s✗%s %s\n" "$ROUGE" "$ZERO" "$1"; ECHECS=$((ECHECS+1)); }
titre(){ printf "\n%s%s%s\n" "$GRIS" "$1" "$ZERO"; }

VERTICALES="expert-comptable avocat notaire cgp banque assurance syndic-copropriete collectivites clinique ehpad medecin industrie sur-mesure"

titre "[C4] Domaine canonique : www partout"
n=$(grep -rl 'canonical" href="https://izaia.fr' --include="*.html" . 2>/dev/null | grep -v '/mockups/' | wc -l)
[ "$n" -eq 0 ] && ok "aucun canonical en non-www" || ko "$n fichier(s) ont encore un canonical en non-www"
n=$(grep -c '<loc>https://izaia.fr' sitemap.xml 2>/dev/null || true)
[ "$n" -eq 0 ] && ok "sitemap : toutes les <loc> en www" || ko "sitemap : $n <loc> encore en non-www"
grep -q 'Sitemap: https://www.izaia.fr/sitemap.xml' robots.txt \
  && ok "robots.txt pointe le sitemap en www" || ko "robots.txt : ligne Sitemap encore en non-www"
n=$(grep -rl 'og:url" content="https://izaia.fr' --include="*.html" . 2>/dev/null | grep -v '/mockups/' | wc -l)
[ "$n" -eq 0 ] && ok "aucun og:url en non-www" || ko "$n fichier(s) ont un og:url en non-www"

titre "[C5] Aucun lien mort dans le pied de page de l'accueil"
# Motif large : les liens morts ne s'ecrivent pas tous <a href="#">.
# Les logos portaient class="logo" avant href, et echappaient au motif etroit.
n=$(grep -coE '<a[^>]*href="#"' index.html 2>/dev/null || true)
[ "$n" -eq 0 ] && ok "plus aucun href=\"#\" dans index.html" || ko "$n lien(s) href=\"#\" subsistent dans index.html"
grep -q 'href="/blog/"' index.html && ok "l'accueil lie /blog/" || ko "l'accueil ne lie pas /blog/"
grep -q 'href="/faq/"'  index.html && ok "l'accueil lie /faq/"  || ko "l'accueil ne lie pas /faq/"
grep -q 'href="/tarif/"' index.html && ok "l'accueil lie /tarif/" || ko "l'accueil ne lie pas /tarif/"

titre "[C6] Le hub /formation/ couvre les 13 verticales"
for v in $VERTICALES; do
  grep -q "href=\"\.\./$v/\"" formation/index.html \
    && ok "/formation/ lie $v" || ko "/formation/ ne lie pas $v"
done

titre "[C1] Le menu des pages 2026 mene aux 13 verticales"
# Les 12 pages au gabarit 2026 : l'accueil et les 11 verticales refondues.
# notaire et medecin sont restees au gabarit precedent : elles relevent du bloc V1.
PAGES_V2="index.html assurance/index.html avocat/index.html banque/index.html cgp/index.html clinique/index.html collectivites/index.html ehpad/index.html expert-comptable/index.html industrie/index.html sur-mesure/index.html syndic-copropriete/index.html"
for f in $PAGES_V2; do
  [ -f "$f" ] || { ko "$f : fichier absent"; continue; }
  # On ne cherche QUE dans le bloc de menu : un lien present ailleurs
  # dans la page (pied de page, corps) ne doit pas faire passer l'assertion.
  bloc=$(awk '/class="nav-metiers"/,/<\/li>/' "$f")
  if [ -z "$bloc" ]; then ko "$f : pas d'entree nav-metiers dans le menu"; continue; fi
  manquants=0
  for v in $VERTICALES; do
    echo "$bloc" | grep -qF "href=\"/$v/\"" || manquants=$((manquants+1))
  done
  [ "$manquants" -eq 0 ] && ok "$f : menu deroulant complet (13 verticales)"     || ko "$f : $manquants verticale(s) absente(s) du menu deroulant"
done

titre "[C1] Le nav-drop « Par metier » couvre les 13 verticales"
# Detection par le libelle du nav-drop : sante/index.html porte un nav-drop
# « Sante » volontairement different, il est hors perimetre.
# Motif volontairement tronque avant l'accent : sous Git Bash, "e accent"
# fait deux octets, et ni [eé] ni "m.tier" ne correspondent.
for f in $(grep -rl 'nav-drop-label">Par m' --include="index.html" . 2>/dev/null | grep -v '/mockups/'); do
  prof=$(echo "${f#./}" | awk -F/ '{print NF-1}')
  pre=""; i=0; while [ "$i" -lt "$prof" ]; do pre="../$pre"; i=$((i+1)); done
  manquants=0
  for v in $VERTICALES; do
    grep -qF "href=\"$pre$v/\"" "$f" || manquants=$((manquants+1))
  done
  [ "$manquants" -eq 0 ] && ok "${f#./} : nav-drop complet" || ko "${f#./} : $manquants verticale(s) absente(s) du nav-drop"
done

titre "[C2] Profondeur : toute page du sitemap à 1 clic de l'accueil"
python verif/profondeur.py || ECHECS=$((ECHECS+1))

titre "[A1] Fil d'Ariane sur les treize verticales"
for v in $VERTICALES; do
  if grep -q 'class="fil-ariane' "$v/index.html" && grep -q '"@type": *"BreadcrumbList"' "$v/index.html"; then
    ok "$v : fil d'Ariane et BreadcrumbList"
  else
    ko "$v : fil d'Ariane ou BreadcrumbList absent"
  fi
done

titre "[A6] Les verticales sont aussi dans le menu mobile du gabarit herite"
# Le menu mobile de ces pages est ecrit a la main, separe du nav-drop :
# compter les liens dans le fichier ne suffit pas a prouver qu'il est a jour.
for f in $(grep -rl 'class="mobile-menu"' --include="index.html" . 2>/dev/null | grep -v '/mockups/'); do
  n=$(grep -c 'class="mm-metier"' "$f" || true)
  [ "${n:-0}" -eq 13 ] && ok "${f#./} : 13 verticales au menu mobile"     || ko "${f#./} : ${n:-0}/13 verticales au menu mobile"
done

titre "[C3] Données structurées sur l'accueil"
n=$(grep -c 'application/ld+json' index.html 2>/dev/null || true)
[ "$n" -ge 1 ] && ok "index.html expose $n bloc(s) JSON-LD" || ko "index.html n'expose aucun JSON-LD"
grep -q '"@type": *"Organization"' index.html && ok "Organization présent" || ko "Organization absent"
grep -q '"@type": *"FAQPage"'     index.html && ok "FAQPage présent"     || ko "FAQPage absent"

if [ "${1:-}" = "--prod" ]; then
  titre "[PROD] Cohérence en ligne"
  code=$(curl -s -o /dev/null -w '%{http_code}' https://izaia.fr/)
  [ "$code" = "308" ] && ok "izaia.fr redirige en 308 (permanent)" \
    || ko "izaia.fr redirige en $code — un 308 est attendu (décision D3, côté Vercel)"
  can=$(curl -sL https://www.izaia.fr/ | grep -oE 'canonical" href="[^"]*"' | head -1)
  echo "$can" | grep -q 'www.izaia.fr' && ok "canonical de la prod en www" || ko "canonical de la prod : $can"
  for u in / /formation/ /tarif/ /faq/ /blog/ /notaire/ /medecin/; do
    c=$(curl -s -o /dev/null -w '%{http_code}' "https://www.izaia.fr$u")
    [ "$c" = "200" ] && ok "$u répond 200" || ko "$u répond $c"
  done
fi

printf "\n"
titre "[A9] Le pied de page commun a toute sa feuille de style"
# Le balisage transplante utilise des classes qui n'existaient pas dans
# common.css : le symbole du logo s'affichait a sa taille intrinseque et le
# bouton de rendez-vous rendait en texte nu.
for c in logo-mark btn-gold foot-top foot-villes; do
  n=$(grep -c "$c" styles/common.css || true)
  [ "${n:-0}" -gt 0 ] && ok "common.css definit .$c" || ko "common.css ne definit pas .$c"
done
grep -q 'nav-cta .btn{white-space:nowrap}' styles/izaia-2026.css   && ok "le bouton de rendez-vous ne se coupe jamais"   || ko "le bouton de rendez-vous peut passer a la ligne"

titre "[A8] Un seul pied de page, ferme correctement"
# Le site en comptait treize variantes. Celui de l'accueil est desormais
# le seul ; trois pages ouvraient meme un <footer> sans jamais le fermer.
ref=$(grep -c 'foot-villes' index.html || true)
manque=0; nonferme=0
for f in $(find . -name "*.html" -not -path "./mockups/*" -not -name "google*" -not -name "design-2026.html" -not -name "hero-*.html" -not -name "mockups-hero.html" -not -path "./realisations/cockpit-demo.html"); do
  o=$(grep -c '<footer' "$f" || true); c=$(grep -c '</footer>' "$f" || true)
  [ "${o:-0}" -ne "${c:-0}" ] && { ko "${f#./} : $o <footer> pour $c </footer>"; nonferme=$((nonferme+1)); }
  [ "${o:-0}" -gt 0 ] && [ "$(grep -c 'foot-villes' "$f" || true)" -eq 0 ] && { ko "${f#./} : pied de page different de celui de l accueil"; manque=$((manque+1)); }
done
[ "$manque" -eq 0 ] && [ "$nonferme" -eq 0 ] && ok "toutes les pages partagent le pied de page de l accueil"

titre "[A7] Charte unique : plus aucune trace de l ancienne palette"
ANCIENNES='#FDFAF6|#F7F3EC|#F2EBE0|#F1EADD|#C2410C|#1C1917|#1C1813|#78716C|#5B5349|#FED7AA|#E89B6C|#EFE4D7|#211B15'
n=$(grep -rEoh "$ANCIENNES" --include="*.html" --include="*.css" --exclude-dir=mockups . 2>/dev/null | wc -l)
[ "${n:-0}" -eq 0 ] && ok "aucune couleur de l ancienne palette" || ko "$n couleur(s) de l ancienne palette subsistent"
RGB='rgba?\([[:space:]]*(194,[[:space:]]*65,[[:space:]]*12|253,[[:space:]]*250,[[:space:]]*246|120,[[:space:]]*113,[[:space:]]*108)'
n=$(grep -rEoh "$RGB" --include="*.html" --include="*.css" --exclude-dir=mockups . 2>/dev/null | wc -l)
[ "${n:-0}" -eq 0 ] && ok "aucune ancienne couleur en notation rgb" || ko "$n ancienne(s) couleur(s) en rgb"
n=$(grep -rloh "Instrument Serif" --include="*.html" --include="*.css" --exclude-dir=mockups . 2>/dev/null | wc -l)
[ "${n:-0}" -eq 0 ] && ok "plus aucune reference a Instrument Serif" || ko "$n fichier(s) referencent encore Instrument Serif"

titre "[A5] Une seule graphie de la marque dans les metadonnees"
# --exclude-dir et non « grep -v /mockups/ » : avec -h, grep supprime les noms
# de fichiers, et le filtre par chemin ne peut donc rien filtrer du tout.
META='<title>[^<]*</title>|<meta name="description" content="[^"]*"|<meta property="og:[a-z:]+" content="[^"]*"'
autres=$(grep -rhoE "$META" --include="*.html" --exclude-dir=mockups . 2>/dev/null | grep -cowE "IZAIA|Izaia" || true)
[ "${autres:-0}" -eq 0 ] && ok "aucune graphie divergente dans les metadonnees" || ko "$autres ligne(s) de metadonnees avec une graphie divergente"

if [ "$ECHECS" -eq 0 ]; then printf "%sTout passe.%s\n" "$VERT" "$ZERO"; exit 0
else printf "%s%d assertion(s) en échec.%s\n" "$ROUGE" "$ECHECS" "$ZERO"; exit 1; fi
