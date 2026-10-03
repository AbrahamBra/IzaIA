# -*- coding: utf-8 -*-
"""Enregistre une demonstration animee en MP4, avec sa voix, pour la faire valider.

    python tools/dossiers/film.py tri-demandes            # -> Telechargements/IZAIA-tri-demandes.mp4
    python tools/dossiers/film.py tri-demandes --images   # + une image par scene, pour controle

Le script sert lui-meme le site en local, ouvre la page qui porte la demonstration,
la passe en plein cadre (1280 x 720), la lance et filme jusqu'au logo de fin.
La voix est ensuite posee sur l'image, calee sur l'instant ou l'audio a demarre.
Demande Playwright (python -m playwright install chromium) et ffmpeg.
"""
import functools
import glob
import http.server
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time

from playwright.sync_api import sync_playwright

import demos

L, H = 1280, 720


class Silencieux(http.server.SimpleHTTPRequestHandler):
    # Le journal des requetes part sur la sortie d'erreur : si elle est fermee
    # (sortie redirigee vers head, par exemple), la requete de l'audio echoue.
    def log_message(self, *args):
        pass


def servir():
    gestion = functools.partial(Silencieux, directory=demos.SITE)
    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), gestion)
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    return serveur


def filmer(nom, sortie, images=False):
    page_dossier, _, etapes = demos.DEMOS[nom]
    sel = '.demo[data-src*="%s"]' % nom
    plein = ("%s .demo-scene{position:fixed !important;inset:0 !important;z-index:99999;"
             "border-radius:0 !important;aspect-ratio:auto !important}"
             "%s :is(.demo-lire,.demo-barre,.demo-avance){display:none !important}") % (sel, sel)
    serveur = servir()
    url = "http://127.0.0.1:%d/%s/" % (serveur.server_address[1], page_dossier.replace(os.sep, "/"))
    brut = tempfile.mkdtemp(prefix="film-")
    with sync_playwright() as p:
        nav = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        avant = time.time()
        ctx = nav.new_context(viewport={"width": L, "height": H}, record_video_dir=brut,
                              record_video_size={"width": L, "height": H})
        page = ctx.new_page()
        apres = time.time()
        erreurs = []
        page.on("pageerror", lambda e: erreurs.append(str(e)))
        page.add_init_script("const A = window.Audio; window.Audio = function(s){"
                             " const a = new A(s); window.__audio = a; return a; };")
        page.goto(url)
        page.wait_for_load_state("networkidle")
        # Sur une carte repliee, la demonstration n'est pas visible : on l'ouvre.
        page.evaluate("(s) => { const d = document.querySelector(s).closest('details'); if (d) d.open = true; }", sel)
        page.locator(sel).first.scroll_into_view_if_needed()
        page.add_style_tag(content=plein)
        page.wait_for_timeout(800)
        duree = float(page.evaluate("(s) => document.querySelector(s).dataset.duree", sel))
        debuts = [float(x) for x in page.evaluate("(s) => document.querySelector(s).dataset.debuts", sel).split()]
        page.evaluate("(s) => document.querySelector(s + ' .demo-lire').click()", sel)
        limite = time.time() + 20
        while True:
            pos = page.evaluate("window.__audio ? window.__audio.currentTime : 0")
            if pos > 0:
                depart = time.time() - pos
                break
            if time.time() > limite:
                raise SystemExit("la voix de %s n'a pas demarre en 20 s" % nom)
            page.wait_for_timeout(20)
        page.wait_for_timeout(int((duree + 2.0) * 1000))
        etat = page.evaluate("(s) => document.querySelector(s).className", sel)
        ctx.close()
        nav.close()
    serveur.shutdown()
    video = glob.glob(os.path.join(brut, "*.webm"))[0]
    mp3 = os.path.join(demos.SITE, page_dossier, "demos", nom + ".mp3")
    subprocess.check_call([
        "ffmpeg", "-y", "-loglevel", "error", "-ss", "%.3f" % (depart - (avant + apres) / 2), "-i", video,
        "-i", mp3, "-t", "%.2f" % (duree + 1.5), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
        "-r", "30", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", sortie])
    shutil.rmtree(brut, ignore_errors=True)
    print(nom, "|", etat, "|", round(duree, 1), "s | erreurs :", erreurs or "aucune", "|", sortie)
    if images:
        # Une image aux deux tiers de chaque scene : c'est la qu'un texte qui deborde se voit.
        bornes = debuts + [duree]
        for i in range(len(debuts)):
            t = bornes[i] + (bornes[i + 1] - bornes[i]) * 0.66
            image = sortie[:-4] + "-scene%d.png" % (i + 1)
            subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-ss", "%.2f" % t, "-i", sortie,
                                   "-frames:v", "1", image])
            print("  ", image)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1 or args[0] not in demos.DEMOS:
        raise SystemExit(__doc__ + "\nDemonstrations : " + ", ".join(demos.DEMOS))
    sortie = os.path.join(os.path.expanduser("~"), "Downloads", "IZAIA-%s.mp4" % args[0])
    filmer(args[0], sortie, images="--images" in sys.argv)
