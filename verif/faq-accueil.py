"""Génère le bloc FAQPage de l'accueil à partir des <details> visibles.

Le schéma ne doit jamais contenir une question absente de la page :
l'extraction depuis le HTML rend la divergence impossible par construction.
"""
import html as htmlmod
import json, os, re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
source = open(os.path.join(RACINE, "index.html"), encoding="utf-8").read()

# Les trois blocs de questions de l'accueil.
zone = re.search(r'<div class="trio-faq">.*</div>\s*</section>', source, re.S)
if not zone:
    raise SystemExit("ARRET : bloc trio-faq introuvable.")

def texte(fragment):
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", htmlmod.unescape(fragment)).strip()

questions = []
# [^<]* et non .*? : avec .*? le moteur peut retro-agir par-dessus le
# balisage et avaler « Voir les N autres questions » PUIS la vraie question
# qui suit, ce qui faisait perdre les trois premieres questions repliees.
motif = re.compile(
    r"<summary>(?P<q>[^<]*)</summary>\s*"
    r'<div class="tf-a">(?P<r>.*?)</div>',
    re.S,
)
for m in motif.finditer(zone.group(0)):
    q, r = texte(m.group("q")), texte(m.group("r"))
    if q.startswith("Voir les") or not r:
        continue          # libellé de dépliage, pas une question
    questions.append({
        "@type": "Question",
        "name": q,
        "acceptedAnswer": {"@type": "Answer", "text": r},
    })

if len(questions) != 23:
    raise SystemExit(f"ARRET : {len(questions)} questions extraites, 23 attendues.")

bloc = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": questions,
}
sortie = os.path.join(RACINE, "verif", "faqpage.json")
with open(sortie, "w", encoding="utf-8") as fh:
    json.dump(bloc, fh, ensure_ascii=False, indent=2)
print(f"{len(questions)} questions extraites vers verif/faqpage.json")
for q in questions:
    print("  ·", q["name"][:78])
