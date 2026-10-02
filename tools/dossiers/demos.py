# -*- coding: utf-8 -*-
"""Les demonstrations animees des cartes d'exemples.

Une demonstration, c'est un dessin (demos/<nom>.svg), une voix off et son
minutage (demos/<nom>.json). La voix dit une phrase par scene ; le minutage
donne l'instant ou chaque phrase commence, et c'est lui qui fait avancer le
dessin. Le lecteur est styles/demo-agent.js.

La narration suit toujours la meme trame, en quatre temps :
    1. Aujourd'hui, ...                la situation de depart
    2. Demain, a l'aide d'un agent IA  ce que l'agent IA produit
    3. le benefice                     ce que cela change pour l'agent municipal
    4. IZAIA est la pour ...           ce que nous faisons

    python tools/dossiers/demos.py voix pv-seance   # (re)genere la voix et le minutage
    python tools/dossiers/exemples_coll.py          # regreffe les cartes
    python tools/dossiers/assembler.py coll-agents

La cle ElevenLabs se lit dans le fichier .env du dossier parent du site, hors
du depot : ELEVENLABS_API_KEY=...
"""
import base64
import html
import io
import json
import os
import re
import subprocess
import sys
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(ICI))
DOSSIER = os.path.join(ICI, "demos")

# Voix francaise de la bibliotheque ElevenLabs : l'API ne la sert qu'aux comptes
# abonnes. En offre gratuite, prendre une voix standard (« Daniel - Steady
# Broadcaster » lit le francais avec le modele multilingue).
VOIX = "Voix Nicolas Petit IA AUDIO Narration"
MODELE = "eleven_multilingual_v2"

# Ce que la voix doit lire autrement que ce qui s'ecrit (meme regle que la VSL).
PRONONCIATION = [(r"\bIZAIA\b", "Izaïa")]

# Dans un dessin, l'endroit ou vient la scene IZAIA (demos/_izaia.svg).
MARQUE = "<!-- IZAIA -->"

# Apres la voix, le logo s'anime seul pendant quelques secondes.
LOGO = 4.5

# Une animation part un peu avant le mot qui la declenche.
AVANCE = 0.15

# La derniere scene est la meme dans toutes les demonstrations : c'est la signature.
FIN = ("IZAIA est là pour vous aider à choisir. Nous regardons d'abord si un produit fait déjà ce travail. "
       "Nous ne construisons un agent IA que s'il le faut. Et nous vous disons quand il n'est pas à construire : "
       "quand il est question de relation humaine, d'arbitrage, de décision. "
       "Là, l'intelligence dont vous avez besoin n'a rien d'artificiel.")
MOTS_FIN = ["vous aider à choisir", "regardons d'abord", "ne construisons", "nous vous disons", "Là, l'intelligence"]

# nom : (dossier de la page, etapes).
# Une etape = (repere affiche, phrase dite, mots qui declenchent une animation).
# Le dessin retrouve l'instant du n-ieme mot de la scene s dans --c<s>-<n>.
DEMOS = {
    "pv-seance": (os.path.join("collectivites", "agents-ia"), [
        ("Aujourd'hui",
         "Aujourd'hui, après chaque conseil, quelqu'un dans votre mairie réécoute la séance pour écrire le procès-verbal.",
         []),
        ("Demain",
         "Demain, vous confiez l'enregistrement à un agent IA. Il vous rend un projet de procès-verbal, dans votre trame : l'ordre du jour, les interventions, les votes.",
         ["Il vous rend", "votre trame", "l'ordre du jour", "les interventions", "les votes"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il n'a plus à tout réécouter ni à tout retaper. Il part d'un texte déjà écrit et vérifie que la transcription est bonne : l'exactitude d'un vote, l'orthographe d'un nom de famille, les chiffres clés. C'est du temps libéré sur une tâche chronophage, et réinvesti au service de vos administrés.",
         ["tout réécouter", "tout retaper", "vérifie", "d'un vote", "d'un nom", "les chiffres", "du temps libéré"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
    "tri-demandes": (os.path.join("collectivites", "agents-ia"), [
        ("Aujourd'hui",
         "Aujourd'hui, les courriels et les formulaires du site arrivent dans la même messagerie. Quelqu'un dans votre mairie les ouvre un par un pour les transmettre au bon service.",
         ["les ouvre un par un"]),
        ("Demain",
         "Demain, un agent IA lit chaque demande écrite et vous propose le service à qui la transmettre : un permis de construire part à l'urbanisme, un nid-de-poule à la voirie, une inscription à la cantine aux écoles.",
         ["lit chaque demande", "un permis de construire", "un nid-de-poule", "une inscription"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il n'a plus à trier chaque message à la main. Il valide le service proposé, ou en choisit un autre. C'est du temps libéré sur une tâche répétitive, et réinvesti au service de vos administrés.",
         ["trier chaque message", "Il valide", "en choisit un autre", "du temps libéré"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
}


def dit(phrase):
    for motif, lecture in PRONONCIATION:
        phrase = re.sub(motif, lecture, phrase)
    return phrase


def bloc(nom):
    """Le HTML de la demonstration, a glisser dans la carte."""
    _, etapes = DEMOS[nom]
    with io.open(os.path.join(DOSSIER, nom + ".svg"), encoding="utf-8") as fh:
        dessin = fh.read().strip()
    # La derniere scene est la meme partout : c'est la signature.
    with io.open(os.path.join(DOSSIER, "_izaia.svg"), encoding="utf-8") as fh:
        assert dessin.count(MARQUE) == 1, "repere de la scene IZAIA absent de %s.svg" % nom
        dessin = dessin.replace(MARQUE, fh.read().strip())
    with io.open(os.path.join(DOSSIER, nom + ".json"), encoding="utf-8") as fh:
        minutage = json.load(fh)
    assert minutage["phrases"] == [e[1] for e in etapes] and minutage["mots"] == [e[2] for e in etapes], (
        "la voix de %s ne dit plus le texte : relancer demos.py voix %s" % (nom, nom))
    cles = ";".join("--c%d-%d:%.3f" % (s + 1, n + 1, q)
                    for s, scene in enumerate(minutage["cles"]) for n, q in enumerate(scene))
    e = html.escape
    l = []
    # La derniere scene, le logo, commence quand la voix s'arrete.
    total = minutage["duree"] + LOGO
    l.append('<div class="demo" data-scene="0" data-src="demos/%s.mp3" data-debuts="%s" data-voix="%.2f" data-duree="%.2f" style="%s">'
             % (nom, " ".join("%.2f" % d for d in minutage["debuts"] + [minutage["duree"]]),
                minutage["duree"], total, cles))
    l.append('  <div class="demo-scene">')
    l.append("    " + dessin.replace("\n", "\n    "))
    l.append('    <button type="button" class="demo-lire">')
    l.append('      <span class="demo-ico" aria-hidden="true"></span>')
    l.append('      <span class="demo-lib">Ce que cet agent IA vous apporte</span>')
    l.append('      <span class="demo-dur">%d s, avec le son</span>' % round(total))
    l.append('    </button>')
    l.append('    <span class="demo-avance" aria-hidden="true"></span>')
    l.append('    <div class="demo-barre">')
    l.append('      <button type="button" class="demo-pp" aria-label="Lire" title="Lire">'
             '<svg viewBox="0 0 16 16" aria-hidden="true"><path class="i-lire" d="M4.5 2.5v11l9-5.5z"/>'
             '<path class="i-pause" d="M4 2.5h3v11H4zM9 2.5h3v11H9z"/></svg></button>')
    l.append('      <button type="button" class="demo-debut" aria-label="Revenir au début" title="Revenir au début">'
             '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 2.5h2v11H3zM13.5 2.5v11L6 8z"/></svg></button>')
    l.append('      <input class="demo-temps" type="range" min="0" max="1000" value="0" aria-label="Position dans la vidéo">')
    l.append('      <span class="demo-chrono">0:00 / %s</span>' % "%d:%02d" % divmod(round(total), 60))
    l.append('    </div>')
    l.append('  </div>')
    l.append('  <ol class="demo-etapes">')
    for etape in etapes:
        l.append("    <li>%s</li>" % e(etape[0], quote=False))
    l.append('  </ol>')
    l.append('  <p class="demo-st" aria-live="off">')
    for etape in etapes:
        l.append("    <span>%s</span>" % e(etape[1], quote=False))
    l.append('  </p>')
    l.append('</div>')
    return "\n".join(l)


def cle():
    chemin = os.path.join(os.path.dirname(SITE), ".env")
    with io.open(chemin, encoding="utf-8-sig") as fh:
        for ligne in fh:
            if ligne.strip().startswith("ELEVENLABS_API_KEY="):
                return ligne.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("ELEVENLABS_API_KEY absente de " + chemin)


def appel(chemin, corps=None):
    req = urllib.request.Request(
        "https://api.elevenlabs.io" + chemin,
        data=json.dumps(corps).encode("utf-8") if corps is not None else None,
        headers={"xi-api-key": cle(), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def voix(nom):
    page, etapes = DEMOS[nom]
    lues = [dit(e[1]) for e in etapes]
    texte = " ".join(lues)
    ident = [v["voice_id"] for v in appel("/v1/voices")["voices"] if v["name"] == VOIX]
    assert ident, "voix introuvable : " + VOIX
    rep = appel("/v1/text-to-speech/%s/with-timestamps?output_format=mp3_44100_128" % ident[0], {
        "text": texte, "model_id": MODELE,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    })
    al = rep["alignment"]
    assert "".join(al["characters"]) == texte, "l'alignement ne suit pas le texte"
    instants = al["character_start_times_seconds"]
    duree = round(al["character_end_times_seconds"][-1], 2)
    debuts, positions, position = [], [], 0
    for lue in lues:
        debuts.append(round(instants[position], 2))
        positions.append(position)
        position += len(lue) + 1
    # Chaque mot declencheur devient une fraction de la duree de sa scene.
    cles = []
    for s, (etape, lue) in enumerate(zip(etapes, lues)):
        fin = debuts[s + 1] if s + 1 < len(debuts) else duree
        scene = []
        for mot in etape[2]:
            assert lue.count(mot) == 1, "mot declencheur absent ou ambigu : %s" % mot
            instant = instants[positions[s] + lue.index(mot)] - AVANCE
            scene.append(round(max(0.0, (instant - debuts[s]) / (fin - debuts[s])), 3))
        cles.append(scene)
    cible = os.path.join(SITE, page, "demos")
    os.makedirs(cible, exist_ok=True)
    brut = os.path.join(DOSSIER, nom + ".brut.mp3")
    with open(brut, "wb") as fh:
        fh.write(base64.b64decode(rep["audio_base64"]))
    # Une voix seule n'a pas besoin de stereo : mono a 64 kbit/s, moitie moins lourd.
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", brut, "-ac", "1", "-b:a", "64k",
                           os.path.join(cible, nom + ".mp3")])
    os.remove(brut)
    with io.open(os.path.join(DOSSIER, nom + ".json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"phrases": [e[1] for e in etapes], "mots": [e[2] for e in etapes],
                   "debuts": debuts, "cles": cles, "duree": duree}, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(nom, ":", len(texte), "caracteres,", duree, "s, debuts", debuts, "cles", cles)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "voix" and sys.argv[2] in DEMOS:
        voix(sys.argv[2])
    else:
        raise SystemExit(__doc__)
