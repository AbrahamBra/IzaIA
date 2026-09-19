"""Génère la voix de la VSL avec Chatterbox Multilingual (Resemble AI, licence MIT).

    vsl/outils/.venv-voix/Scripts/python vsl/outils/voix_chatterbox.py [--reference chemin.wav] [--refaire 12,13]
    vsl/outils/.venv-voix/Scripts/python vsl/outils/voix_chatterbox.py --verifier     (liste les prises douteuses)
    vsl/outils/.venv-voix/Scripts/python vsl/outils/voix_chatterbox.py --refaire douteuses

Une prise par sous-titre dans vsl/outils/prises/ (001.wav, 002.wav…). Les prises déjà présentes
sont conservées : on peut interrompre et relancer, ou ne refaire que certaines phrases (--refaire).
Ensuite, assembler et recaler la vidéo :

    python vsl/outils/voix_temoin.py --prises

--reference : dix secondes de voix française, propre, sans musique. Le timbre est reproduit.
N'utiliser que la voix d'une personne qui a donné son accord écrit.
Sans référence, c'est la voix par défaut du modèle.

Chaque fichier porte le tatouage inaudible ajouté par Chatterbox (Perth).
"""
import re
import sys
import wave
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from voix_temoin import PRISES, lire_scenes  # noqa: E402

# Forme écrite -> forme dite. Les sous-titres gardent la forme écrite.
DICTION = [
    (r"ChatGPT", "Tchat GPT"),
    (r"\bIZAIA\b", "Izaïa"),
    (r"\bIA\b\.?", "I.A."),
    (r"FORM'RH", "Forme R.H."),
    (r"\bOPCO\b", "Opco"),
    (r"\bemails\b", "e-mails"),
    (r"[«»]", ""),
]
GRAINE = 7

# Le modèle ajoute parfois une queue de sons parasites, ou avale des mots. Le débit le trahit :
# une phrase dite normalement tourne autour de 15 caractères par seconde.
DEBIT_MIN, DEBIT_MAX, DEBIT_CIBLE = 11.5, 26.0, 17.0
ESSAIS = 5


def debit(texte, secondes):
    return len(texte) / max(0.1, secondes)


def duree(chemin):
    with wave.open(str(chemin), "rb") as w:
        return w.getnframes() / w.getframerate()


def douteuses(phrases):
    out = []
    for i, p in enumerate(phrases, 1):
        f = PRISES / f"{i:03d}.wav"
        if f.exists() and not DEBIT_MIN <= debit(dire(p), duree(f)) <= DEBIT_MAX:
            out.append(i)
    return out


def dire(texte):
    texte = texte.replace(" ", " ")
    for motif, dit in DICTION:
        texte = re.sub(motif, dit, texte)
    return re.sub(r"\s+", " ", texte).strip()


def rogner(x, sr, seuil=0.01, marge=0.06):
    """Retire le silence en tête et en queue, garde une courte marge."""
    fort = np.flatnonzero(np.abs(x) > seuil)
    if fort.size == 0:
        return x
    m = int(marge * sr)
    return x[max(0, fort[0] - m): fort[-1] + m]


def ecrire(chemin, x, sr):
    x = x / max(1e-6, np.abs(x).max()) * 0.89  # même niveau d'une prise à l'autre
    with wave.open(str(chemin), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def main():
    args = sys.argv[1:]
    reference = args[args.index("--reference") + 1] if "--reference" in args else None
    phrases = [c for s in lire_scenes() for c in s["caps"]]
    if "--verifier" in args:
        for i in douteuses(phrases):
            t = dire(phrases[i - 1])
            d = duree(PRISES / f"{i:03d}.wav")
            print(f"{i:03d}  {d:4.1f} s  {debit(t, d):4.1f} car/s  {t}")
        return
    refaire = set()
    if "--refaire" in args:
        v = args[args.index("--refaire") + 1]
        refaire = set(douteuses(phrases)) if v == "douteuses" else {int(n) for n in v.split(",")}
    PRISES.mkdir(exist_ok=True)
    a_faire = [i for i in range(1, len(phrases) + 1) if i in refaire or not (PRISES / f"{i:03d}.wav").exists()]
    if not a_faire:
        print("Toutes les prises existent. --refaire 3,4 pour en régénérer.")
        return

    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    modele = ChatterboxMultilingualTTS.from_pretrained(device="cpu")

    for i in a_faire:
        texte = dire(phrases[i - 1])
        options = {"language_id": "fr"}
        if reference:
            options["audio_prompt_path"] = reference
        # Plusieurs essais si le débit est anormal ; on garde le plus proche d'un débit de parole.
        meilleur = None
        for essai in range(ESSAIS):
            torch.manual_seed(GRAINE + i + 1000 * (essai + (1 if i in refaire else 0)))
            wav = modele.generate(texte, **options)
            x = rogner(wav.squeeze().cpu().numpy(), modele.sr)
            d = debit(texte, len(x) / modele.sr)
            if meilleur is None or abs(d - DEBIT_CIBLE) < abs(meilleur[0] - DEBIT_CIBLE):
                meilleur = (d, x)
            if DEBIT_MIN <= d <= DEBIT_MAX:
                break
        d, x = meilleur
        ecrire(PRISES / f"{i:03d}.wav", x, modele.sr)
        alerte = "" if DEBIT_MIN <= d <= DEBIT_MAX else "   << débit anormal, à écouter"
        print(f"{i:03d}/{len(phrases)}  {len(x) / modele.sr:4.1f} s  {d:4.1f} car/s  {texte}{alerte}", flush=True)


if __name__ == "__main__":
    main()
