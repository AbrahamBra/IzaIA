/* ═══════════════════════════════════════════════════════════════
   DEMONSTRATIONS ANIMEES — cartes d'exemples d'agents IA
   ═══════════════════════════════════════════════════════════════
   Une demonstration est un dessin en plusieurs scenes et une voix off.
   La voix fait foi : c'est sa position qui decide de la scene affichee,
   les animations de chaque scene sont en CSS. Sans son (fichier absent,
   lecture refusee), une horloge interne suit le meme minutage.

   Le balisage vient de tools/dossiers/demos.py.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  var demos = Array.prototype.slice.call(document.querySelectorAll('.demo'));
  if (!demos.length) { return; }
  var lecteurs = [];

  demos.forEach(function (demo) {
    var debuts = demo.getAttribute('data-debuts').split(' ').map(Number);
    var duree = Number(demo.getAttribute('data-duree'));
    // La voix s'arrete avant la fin : la derniere scene, le logo, est muette.
    var voix = Number(demo.getAttribute('data-voix')) || duree;
    var bouton = demo.querySelector('.demo-lire');
    var libelle = demo.querySelector('.demo-lib');
    var etapes = Array.prototype.slice.call(demo.querySelectorAll('.demo-etapes li'));
    var phrases = Array.prototype.slice.call(demo.querySelectorAll('.demo-st span'));
    var audio = null, muet = false, t = 0, dernier = 0, image = 0;

    // Chaque scene dure le temps de sa phrase : les delais des animations
    // s'expriment en fractions de cette duree (--s1, --s2...).
    debuts.forEach(function (debut, i) {
      var fin = i + 1 < debuts.length ? debuts[i + 1] : duree;
      demo.style.setProperty('--s' + (i + 1), (fin - debut).toFixed(2) + 's');
    });

    function scene(n) {
      if (demo.getAttribute('data-scene') === String(n)) { return; }
      demo.setAttribute('data-scene', n);
      // Pendant le logo, le dernier repere reste allume.
      etapes.forEach(function (li, i) { li.classList.toggle('courant', i === Math.min(n, etapes.length) - 1); });
      phrases.forEach(function (p, i) { p.classList.toggle('courant', i === n - 1); });
    }

    function etat(nom, texte) {
      demo.classList.toggle('joue', nom === 'joue' || nom === 'pause');
      demo.classList.toggle('pause', nom === 'pause');
      demo.classList.toggle('fini', nom === 'fini');
      libelle.textContent = texte;
      bouton.setAttribute('aria-label', texte);
    }

    function tic(maintenant) {
      if (audio && !muet && !audio.paused) { t = audio.currentTime; }
      else { t += Math.min(0.25, (maintenant - dernier) / 1000); }
      dernier = maintenant;
      if (t >= duree) { finir(); return; }
      demo.style.setProperty('--p', (t / duree).toFixed(4));
      var n = 1;
      debuts.forEach(function (debut, i) { if (t >= debut) { n = i + 1; } });
      scene(n);
      image = requestAnimationFrame(tic);
    }

    function lire() {
      lecteurs.forEach(function (autre) { if (autre !== lecteur) { autre.pause(); } });
      if (!audio) {
        audio = new Audio(demo.getAttribute('data-src'));
        audio.addEventListener('error', function () { muet = true; });
      }
      if (demo.classList.contains('fini') || !demo.classList.contains('joue')) {
        t = 0;
        demo.style.setProperty('--p', '0');
        demo.setAttribute('data-scene', '0');
        try { audio.currentTime = 0; } catch (e) { /* pas encore charge */ }
      }
      etat('joue', 'Mettre en pause');
      if (!muet) { audio.play().catch(function () { muet = true; }); }
      dernier = performance.now();
      cancelAnimationFrame(image);
      image = requestAnimationFrame(tic);
    }

    function pause() {
      if (!demo.classList.contains('joue') || demo.classList.contains('pause')) { return; }
      cancelAnimationFrame(image);
      if (audio) { audio.pause(); }
      etat('pause', 'Reprendre');
    }

    function reprendre() {
      etat('joue', 'Mettre en pause');
      if (audio && !muet && t < voix) { audio.play().catch(function () { muet = true; }); }
      dernier = performance.now();
      image = requestAnimationFrame(tic);
    }

    function finir() {
      cancelAnimationFrame(image);
      if (audio) { audio.pause(); }
      scene(debuts.length);
      demo.style.setProperty('--p', '1');
      etat('fini', 'Revoir');
    }

    bouton.addEventListener('click', function () {
      if (demo.classList.contains('pause')) { reprendre(); }
      else if (demo.classList.contains('joue')) { pause(); }
      else { lire(); }
    });

    // Carte sortie de l'ecran, repliee ou filtree : la voix ne continue pas seule.
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entrees) {
        if (!entrees[0].isIntersecting) { pause(); }
      }).observe(demo);
    }

    var lecteur = { pause: pause };
    lecteurs.push(lecteur);
  });
})();
