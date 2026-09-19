"""Génère la voix témoin de la VSL et le minutage qui va avec.

    python vsl/outils/voix_temoin.py

Lit les sous-titres dans vsl/expert-comptable/lecteur.html (la page reste la seule source du texte),
fait dire chaque phrase par la voix Windows « Hortense », assemble le tout, et écrit :

    vsl/expert-comptable/voix.mp3   la piste audio
    vsl/expert-comptable/voix.js    le début de chaque scène et de chaque sous-titre, en secondes

La voix Windows est une voix de travail : elle sert à caler la vidéo, pas à la diffuser.
Pour une voix définitive, enregistrer phrase par phrase dans vsl/outils/prises/ (001.wav, 002.wav…,
même ordre que les sous-titres, wav mono) puis relancer avec --prises : le minutage est recalculé.

Dépendances : Windows (System.Speech), ffmpeg dans le PATH.
"""
import json
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

VSL = Path(__file__).resolve().parents[1]
PAGE = VSL / "expert-comptable" / "lecteur.html"
MP3 = VSL / "expert-comptable" / "voix.mp3"
MARKS = VSL / "expert-comptable" / "voix.js"
PRISES = Path(__file__).resolve().parent / "prises"

AMORCE = 0.4          # silence avant la première phrase
ENTRE_PHRASES = 0.28
ENTRE_SCENES = 0.9
FIN = 3.0             # l'écran de fin reste affiché, le bouton de RDV aussi

# Forme écrite -> forme dite. Les sous-titres gardent la forme écrite.
DICTION = [
    (r"ChatGPT", "Tchat G P T"),
    (r"\bIZAIA\b", "Izaïa"),
    (r"\bIA\b", "I A"),
    (r"FORM'RH", "Forme R H"),
    (r"\bOPCO\b", "Opco"),
    (r"\bemails\b", "e-mails"),
    (r"[«»]", ""),
]


def lire_scenes():
    html = PAGE.read_text(encoding="utf-8")
    scenes = []
    for m in re.finditer(r"\{id:'(s\d+)'.*?caps:\[(.*?)\]\}", html, re.S):
        bloc = m.group(2).replace("'+N+'", " ")
        caps = [c.replace("\\'", "'") for c in re.findall(r"'((?:[^'\\]|\\.)*)'", bloc)]
        scenes.append({"id": m.group(1), "caps": caps})
    if not scenes:
        sys.exit("Aucune scène trouvée dans " + str(PAGE))
    return scenes


def dire(texte):
    texte = texte.replace(" ", " ")
    for motif, dit in DICTION:
        texte = re.sub(motif, dit, texte)
    return texte


def synthese(phrases, dossier):
    """Un wav par phrase, via System.Speech. Un seul appel PowerShell pour tout le lot."""
    travaux = [{"texte": dire(p), "wav": str(dossier / f"{i + 1:03d}.wav")} for i, p in enumerate(phrases)]
    liste = dossier / "travaux.json"
    liste.write_text(json.dumps(travaux, ensure_ascii=False), encoding="utf-8")
    ps = dossier / "synthese.ps1"
    ps.write_text(
        "Add-Type -AssemblyName System.Speech\n"
        "$v = New-Object System.Speech.Synthesis.SpeechSynthesizer\n"
        "$v.SelectVoice('Microsoft Hortense Desktop')\n"
        "$v.Rate = 2\n"  # 0 est lent (135 mots/min) ; 2 approche un débit de conversation
        "$fmt = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(22050, "
        "[System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)\n"
        f"$t = Get-Content -Raw -Encoding UTF8 '{liste}' | ConvertFrom-Json\n"
        "foreach ($j in $t) { $v.SetOutputToWaveFile($j.wav, $fmt); $v.Speak($j.texte) }\n"
        "$v.SetOutputToNull(); $v.Dispose()\n",
        encoding="utf-8-sig",
    )
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps)], check=True)
    return [Path(t["wav"]) for t in travaux]


def main():
    scenes = lire_scenes()
    phrases = [c for s in scenes for c in s["caps"]]

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        if "--prises" in sys.argv:
            clips = sorted(PRISES.glob("*.wav"))
            if len(clips) != len(phrases):
                sys.exit(f"{len(clips)} prises pour {len(phrases)} phrases : il en faut une par sous-titre.")
        else:
            clips = synthese(phrases, tmp)

        with wave.open(str(clips[0]), "rb") as w:
            params = w.getparams()
        octets_par_seconde = params.framerate * params.sampwidth * params.nchannels

        def silence(sec):
            n = int(sec * params.framerate) * params.sampwidth * params.nchannels
            return b"\x00" * n

        piste = bytearray(silence(AMORCE))
        marques, k = [], 0
        for i, s in enumerate(scenes):
            debut_scene = 0.0 if i == 0 else len(piste) / octets_par_seconde - ENTRE_SCENES / 2
            cues = []
            for j, _ in enumerate(s["caps"]):
                with wave.open(str(clips[k]), "rb") as w:
                    if w.getparams()[:3] != params[:3]:
                        sys.exit(f"{clips[k].name} : format différent du premier clip.")
                    cues.append(round(len(piste) / octets_par_seconde, 2))
                    piste += w.readframes(w.getnframes())
                k += 1
                dernier = j == len(s["caps"]) - 1
                piste += silence(ENTRE_SCENES if dernier else ENTRE_PHRASES)
            marques.append({"id": s["id"], "start": round(debut_scene, 2), "cues": cues})
        piste += silence(FIN)
        duree = round(len(piste) / octets_par_seconde, 2)

        brut = tmp / "piste.wav"
        with wave.open(str(brut), "wb") as w:
            w.setparams(params)
            w.writeframes(bytes(piste))
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(brut), "-ac", "1", "-b:a", "80k", str(MP3)],
            check=True,
        )

    MARKS.write_text(
        "// Généré par vsl/outils/voix_temoin.py. Ne pas modifier à la main.\n"
        "window.VSL_VOICE = "
        + json.dumps({"src": MP3.name, "dur": duree, "scenes": marques}, ensure_ascii=False, indent=1)
        + ";\n",
        encoding="utf-8",
    )
    print(f"{len(phrases)} phrases, {duree:.1f} s ({int(duree // 60)} min {int(duree % 60):02d})")
    for m in marques:
        print(f"  {m['id']:>4}  {m['start']:6.1f} s")


if __name__ == "__main__":
    main()
