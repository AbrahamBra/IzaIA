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

# Notariat et Medecins sont sortis du menu : ces deux pages n'ont pas ete
# relues et n'ont pas ete reprises lors de la refonte 2026. Elles restent
# en ligne et indexees, comme les autres pages deliees.
VERTICALES="expert-comptable avocat cgp banque assurance syndic-copropriete collectivites clinique ehpad industrie sur-mesure"

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
grep -q 'href="/blog/"' index.html && ko "l'accueil lie /blog/, deliee volontairement" || ok "/blog/ reste deliee, comme voulu"
grep -q 'href="/faq/"' index.html && ko "l'accueil lie /faq/, deliee volontairement" || ok "/faq/ reste deliee, comme voulu"
# /tarif/ a ete deliee volontairement : son contenu n'est pas termine.
# On verifie donc l'inverse, pour que le lien ne revienne pas par megarde.
grep -q 'href="/tarif/"' index.html && ko "l'accueil lie /tarif/, qui est deliee volontairement"   || ok "/tarif/ reste deliee, comme voulu"

titre "[C6] Le hub /formation/ couvre les verticales du menu"
for v in $VERTICALES; do
  # Chemins absolus depuis que les vignettes viennent de l'accueil,
  # relatifs ailleurs dans la page : on accepte les deux formes.
  motif='href="(/|\.\./)'"$v"'/"'
  grep -qE "$motif" formation/index.html \
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
  [ "$manquants" -eq 0 ] && ok "$f : menu deroulant complet (11 verticales)"     || ko "$f : $manquants verticale(s) absente(s) du menu deroulant"
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

titre "[A1] Fil d'Ariane sur les verticales du menu"
for v in $VERTICALES; do
  if grep -q 'class="fil-ariane' "$v/index.html" && grep -q '"@type": *"BreadcrumbList"' "$v/index.html"; then
    ok "$v : fil d'Ariane et BreadcrumbList"
  else
    ko "$v : fil d'Ariane ou BreadcrumbList absent"
  fi
done

titre "[A6] Les verticales sont aussi dans le menu mobile"
# Le menu mobile de ces pages est ecrit a la main, separe du nav-drop :
# compter les liens dans le fichier ne suffit pas a prouver qu'il est a jour.
for f in $(grep -rl 'class="mobile-menu"' --include="index.html" . 2>/dev/null | grep -v '/mockups/'); do
  n=$(grep -c 'class="mm-metier"' "$f" || true)
  [ "${n:-0}" -eq 11 ] && ok "${f#./} : 11 verticales au menu mobile"     || ko "${f#./} : ${n:-0}/11 verticales au menu mobile"
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
titre "[A11] Le panneau mobile reste hors du flux"
# nav.js ajoute le panneau au <body>, pas dans l en-tete : le cantonner a
# header.site l empechait de recevoir ses regles, et il s affichait en clair
# au bas de chaque page, sous le pied de page.
n=$(grep -c 'header\.site \.nav-panneau\|header\.site \.mm-deplier\|header\.site \.mm-sous' styles/common.css || true)
[ "${n:-0}" -eq 0 ] && ok "les regles du panneau ne sont pas cantonnees a l en-tete"   || ko "$n regle(s) du panneau cantonnee(s) a tort a header.site"
grep -qE '(^|[^ ])\.nav-panneau\{[^}]*position:fixed' styles/common.css   && ok "common.css sort le panneau du flux" || ko "common.css ne sort pas le panneau du flux"

titre "[A10] Une seule barre de navigation, celle de l accueil"
# Les pages heritees avaient leur propre barre : Formation, Conseil,
# Equipe, Articles, Tarifs. Elles portent desormais celle de l accueil.
reste=$(grep -rl 'class="nav" id="navbar"' --include="*.html" --exclude-dir=mockups . 2>/dev/null | wc -l)
[ "${reste:-0}" -eq 0 ] && ok "aucune page ne garde l ancienne barre" || ko "$reste page(s) gardent l ancienne barre"
reste=$(grep -rl 'class="mobile-menu"' --include="*.html" --exclude-dir=mockups . 2>/dev/null | wc -l)
[ "${reste:-0}" -eq 0 ] && ok "aucun ancien panneau mobile" || ko "$reste ancien(s) panneau(x) mobile"
sans=0
for f in $(grep -rl '<header class="site">' --include="*.html" --exclude-dir=mockups . 2>/dev/null); do
  grep -q 'class="topbar"' "$f" || { ko "${f#./} : bandeau d annonce absent"; sans=$((sans+1)); }
  grep -q 'styles/nav.js' "$f" || { ko "${f#./} : script du panneau mobile absent"; sans=$((sans+1)); }
done
[ "$sans" -eq 0 ] && ok "bandeau et script presents sur toutes les pages a en-tete"

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
# Compare la liste des liens plutot qu'une chaine temoin : un marqueur
# unique casse des qu'on retire un bloc, ce qui est arrive avec la ligne
# des villes, deliee parce que ces pages ne sont pas terminees.
python verif/pied-de-page.py || ECHECS=$((ECHECS+1))

titre "[A7] Charte unique : plus aucune trace de l ancienne palette"
ANCIENNES='#FDFAF6|#F7F3EC|#F2EBE0|#F1EADD|#C2410C|#1C1917|#1C1813|#78716C|#5B5349|#FED7AA|#E89B6C|#EFE4D7|#211B15'
n=$(grep -rEoh "$ANCIENNES" --include="*.html" --include="*.css" --exclude-dir=mockups . 2>/dev/null | wc -l)
[ "${n:-0}" -eq 0 ] && ok "aucune couleur de l ancienne palette" || ko "$n couleur(s) de l ancienne palette subsistent"
RGB='rgba?\([[:space:]]*(194,[[:space:]]*65,[[:space:]]*12|253,[[:space:]]*250,[[:space:]]*246|120,[[:space:]]*113,[[:space:]]*108)'
n=$(grep -rEoh "$RGB" --include="*.html" --include="*.css" --exclude-dir=mockups . 2>/dev/null | wc -l)
[ "${n:-0}" -eq 0 ] && ok "aucune ancienne couleur en notation rgb" || ko "$n ancienne(s) couleur(s) en rgb"
n=$(grep -rloh "Instrument Serif" --include="*.html" --include="*.css" --exclude-dir=mockups . 2>/dev/null | wc -l)
[ "${n:-0}" -eq 0 ] && ok "plus aucune reference a Instrument Serif" || ko "$n fichier(s) referencent encore Instrument Serif"

titre "[A14] Aucune ancre ne pointe vers un identifiant absent"
# Le pied de page a ete transplante depuis l'accueil, ses ancres etaient
# restees nues : sur /avocat/, « href="#integrer" » cherchait un id qui
# n'existe que sur l'accueil. 351 liens morts dans les pieds de page, plus
# 125 dans les en-tetes des pages restees sur l'ancienne generation.
python verif/ancres.py || ECHECS=$((ECHECS+1))

titre "[A13] Les pages supprimees ont bien disparu"
# Supprimees les 8 septembre 2026 a la demande du client : contenu non relu
# et pas d'intention de le reprendre. Les cinq URL repondaient 200 en ligne
# et etaient indexees ; une redirection permanente evite d'en faire des
# pages introuvables. Le maillage interne est repare en plus de la
# redirection, pour que le site tienne si vercel.json disparaissait.
for p in notaire medecin tarif programme equipe; do
  [ -d "$p" ] && ko "le dossier $p/ existe encore" || ok "$p/ n existe plus"
  n=$(grep -rl "href=\"[^\"]*/$p/\"" --include="*.html" --exclude-dir=mockups --exclude-dir=realisations --exclude-dir=sante . | wc -l)
  [ "${n:-0}" -eq 0 ] && ok "plus aucun lien interne vers $p" || ko "$n page(s) lient encore $p"
  grep -q "\"/$p/:chemin\*\"" vercel.json     && ok "$p est redirige" || ko "$p n a pas de redirection"
done

titre "[A12] Le formulaire de contact : secteurs et consentement"
# La liste des secteurs doit suivre les pages reellement publiees. Elle
# proposait Notaire — page non relue et deliee — et ignorait la gestion de
# patrimoine et les collectivites, qui ont pourtant leur page en ligne.
for m in "Gestion de patrimoine" "Mairie, collectivité"; do
  grep -q "<option>$m" index.html && ok "le formulaire propose : $m" || ko "le formulaire ignore : $m"
done
grep -q "<option>Notaire</option>" index.html && ko "le formulaire propose encore Notaire, dont la page est deliee" || ok "Notaire ne figure plus dans les secteurs"
# Sans option vide en tete, le premier secteur part coche par defaut et
# toutes les demandes non renseignees arrivent etiquetees expert-comptable.
grep -q '<option value="">' index.html && ok "un choix neutre ouvre la liste des secteurs" || ko "la liste des secteurs demarre sur un secteur reel"
# Le consentement doit etre recueilli, pas seulement annonce.
grep -q 'id="f-consent" type="checkbox" name="consentement" required' index.html && ok "la case de consentement est presente et obligatoire" || ko "le consentement n est pas recueilli par une case obligatoire"
grep -q 'consentement: f.consentement' index.html && ok "le consentement voyage avec la demande" || ko "le consentement n est pas transmis au webhook"
n=$(grep -c '\.f-consent' index.html || true)
[ "${n:-0}" -gt 0 ] && ok "la case de consentement a sa feuille de style" || ko "la case de consentement n est pas stylee"

titre "[A5] Une seule graphie de la marque dans les metadonnees"
# --exclude-dir et non « grep -v /mockups/ » : avec -h, grep supprime les noms
# de fichiers, et le filtre par chemin ne peut donc rien filtrer du tout.
META='<title>[^<]*</title>|<meta name="description" content="[^"]*"|<meta property="og:[a-z:]+" content="[^"]*"'
autres=$(grep -rhoE "$META" --include="*.html" --exclude-dir=mockups . 2>/dev/null | grep -cowE "IZAIA|Izaia" || true)
[ "${autres:-0}" -eq 0 ] && ok "aucune graphie divergente dans les metadonnees" || ko "$autres ligne(s) de metadonnees avec une graphie divergente"

if [ "$ECHECS" -eq 0 ]; then printf "%sTout passe.%s\n" "$VERT" "$ZERO"; exit 0
else printf "%s%d assertion(s) en échec.%s\n" "$ROUGE" "$ECHECS" "$ZERO"; exit 1; fi
