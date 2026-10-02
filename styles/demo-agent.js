/* ═══════════════════════════════════════════════════════════════
   DEMONSTRATIONS ANIMEES — cartes d'exemples d'agents IA
   ═══════════════════════════════════════════════════════════════
   Une demonstration est un dessin en plusieurs scenes et une voix off.
   La voix fait foi : c'est sa position qui decide de la scene affichee,
   les animations de chaque scene sont en CSS. Sans son (fichier absent,
   lecture refusee), une horloge interne suit le meme minutage.

   Le lecteur se comporte comme celui d'une video : une barre apparait au
   survol (au toucher sur telephone) avec lecture, retour au debut, une
   barre de progression qu'on peut faire glisser, et le temps ecoule.

   Le balisage vient de tools/dossiers/demos.py.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  var demos = Array.prototype.slice.call(document.querySelectorAll('.demo'));
  if (!demos.length) { return; }
  var lecteurs = [];

  function chrono(s) {
    s = Math.max(0, Math.round(s));
    return Math.floor(s / 60) + ':' + ('0' + (s % 60)).slice(-2);
  }

  demos.forEach(function (demo) {
    var debuts = demo.getAttribute('data-debuts').split(' ').map(Number);
    var duree = Number(demo.getAttribute('data-duree'));
    // La voix s'arrete avant la fin : la derniere scene, le logo, est muette.
    var voix = Number(demo.getAttribute('data-voix')) || duree;
    var cadre = demo.querySelector('.demo-scene');
    var affiche = demo.querySelector('.demo-lire');
    var bLire = demo.querySelector('.demo-pp');
    var bDebut = demo.querySelector('.demo-debut');
    var curseur = demo.querySelector('.demo-temps');
    var temps = demo.querySelector('.demo-chrono');
    var etapes = Array.prototype.slice.call(demo.querySelectorAll('.demo-etapes li'));
    var phrases = Array.prototype.slice.call(demo.querySelectorAll('.demo-st span'));
    var audio = null, muet = false, t = 0, dernier = 0, image = 0;
    var enLecture = false, glisse = false, veille = 0;

    // Chaque scene dure le temps de sa phrase : les delais des animations
    // s'expriment en fractions de cette duree (--s1, --s2...).
    debuts.forEach(function (debut, i) {
      var fin = i + 1 < debuts.length ? debuts[i + 1] : duree;
      demo.style.setProperty('--s' + (i + 1), (fin - debut).toFixed(2) + 's');
    });

    function sceneA(x) {
      var n = 1;
      debuts.forEach(function (debut, i) { if (x >= debut) { n = i + 1; } });
      return n;
    }

    function scene(n) {
      if (demo.getAttribute('data-scene') === String(n)) { return; }
      demo.setAttribute('data-scene', n);
      // Pendant le logo, le dernier repere reste allume.
      etapes.forEach(function (li, i) { li.classList.toggle('courant', i === Math.min(n, etapes.length) - 1); });
      phrases.forEach(function (p, i) { p.classList.toggle('courant', i === n - 1); });
    }

    // Apres un saut, le dessin se recale : on rejoue la scene et on avance
    // chacune de ses animations jusqu'a l'instant vise.
    function caler() {
      var n = sceneA(t);
      demo.setAttribute('data-scene', '');
      void demo.offsetWidth;
      scene(n);
      void demo.offsetWidth;
      if (!demo.getAnimations) { return; }
      var decalage = (t - debuts[n - 1]) * 1000;
      demo.getAnimations({ subtree: true }).forEach(function (a) {
        try { a.currentTime = decalage; } catch (e) { /* animation deja terminee */ }
      });
    }

    function afficher() {
      demo.style.setProperty('--p', (t / duree).toFixed(4));
      if (!glisse) { curseur.value = Math.round(t / duree * 1000); }
      temps.textContent = chrono(t) + ' / ' + chrono(duree);
    }

    function etat(nom) {
      enLecture = nom === 'joue';
      demo.classList.toggle('joue', nom === 'joue' || nom === 'pause');
      demo.classList.toggle('pause', nom === 'pause');
      demo.classList.toggle('fini', nom === 'fini');
      var texte = nom === 'joue' ? 'Mettre en pause' : (nom === 'fini' ? 'Revoir' : 'Lire');
      bLire.setAttribute('aria-label', texte);
      bLire.title = texte;
    }

    function jouerVoix() {
      // Une lecture interrompue par un rechargement (AbortError) n'est pas un refus.
      if (audio && !muet && t < voix) {
        audio.play().catch(function (e) { if (!e || e.name !== 'AbortError') { muet = true; } });
      }
    }

    function tic(maintenant) {
      if (audio && !muet && !audio.paused) { t = audio.currentTime; }
      else { t += Math.min(0.25, (maintenant - dernier) / 1000); }
      dernier = maintenant;
      if (t >= duree) { finir(); return; }
      scene(sceneA(t));
      afficher();
      image = requestAnimationFrame(tic);
    }

    function demarrer() {
      cancelAnimationFrame(image);
      dernier = performance.now();
      image = requestAnimationFrame(tic);
    }

    function preparer() {
      lecteurs.forEach(function (autre) { if (autre !== lecteur) { autre.pause(); } });
      if (!audio) {
        audio = new Audio(demo.getAttribute('data-src'));
        audio.addEventListener('error', function () { muet = true; });
        // Un serveur qui ne sert pas les requetes partielles rend l'audio
        // impossible a deplacer : on le recharge alors en entier, en memoire.
        audio.addEventListener('loadedmetadata', function () {
          var s = audio.seekable;
          if (s.length && s.end(0) >= audio.duration - 0.5) { return; }
          fetch(audio.currentSrc).then(function (r) { return r.blob(); }).then(function (b) {
            audio.addEventListener('loadedmetadata', function () {
              try { audio.currentTime = Math.min(t, voix); } catch (e) { /* hors limites */ }
              if (enLecture) { jouerVoix(); }
            }, { once: true });
            audio.src = URL.createObjectURL(b);
          }).catch(function () { /* on garde la lecture sans saut */ });
        }, { once: true });
      }
    }

    function recommencer() {
      preparer();
      t = 0;
      audio.pause();
      try { audio.currentTime = 0; } catch (e) { /* pas encore charge */ }
      etat('joue');
      caler();
      afficher();
      jouerVoix();
      demarrer();
      reveiller();
    }

    function lire() {
      if (!demo.classList.contains('joue') || demo.classList.contains('fini')) { recommencer(); return; }
      preparer();
      etat('joue');
      jouerVoix();
      demarrer();
    }

    function pause() {
      if (!enLecture) { return; }
      cancelAnimationFrame(image);
      if (audio) { audio.pause(); }
      etat('pause');
    }

    function finir() {
      cancelAnimationFrame(image);
      if (audio) { audio.pause(); }
      t = duree;
      scene(debuts.length);
      afficher();
      etat('fini');
    }

    function aller(x) {
      t = Math.max(0, Math.min(duree, x));
      if (t >= duree) { finir(); return; }
      if (demo.classList.contains('fini')) { etat('pause'); }
      if (audio) {
        if (t < voix) {
          try { audio.currentTime = t; } catch (e) { /* pas encore charge */ }
          if (enLecture) { jouerVoix(); }
        } else {
          audio.pause();
        }
      }
      caler();
      afficher();
      if (enLecture) { demarrer(); }
    }

    // La barre se montre au survol ou au toucher, et s'efface pendant la lecture.
    function reveiller() {
      demo.classList.add('ctrl');
      clearTimeout(veille);
      veille = setTimeout(function () { if (enLecture && !glisse) { demo.classList.remove('ctrl'); } }, 2600);
    }

    affiche.addEventListener('click', recommencer);
    bLire.addEventListener('click', function () { if (enLecture) { pause(); } else { lire(); } reveiller(); });
    bDebut.addEventListener('click', recommencer);
    curseur.addEventListener('input', function () {
      glisse = true;
      aller(curseur.value / 1000 * duree);
      reveiller();
    });
    curseur.addEventListener('change', function () { glisse = false; reveiller(); });
    // Seule une vraie souris fait apparaitre la barre au survol : un doigt
    // genere aussi des mouvements, qu'on ignore ici.
    cadre.addEventListener('pointermove', function (e) { if (e.pointerType === 'mouse') { reveiller(); } });
    cadre.addEventListener('focusin', reveiller);
    cadre.addEventListener('mouseleave', function () { if (enLecture) { demo.classList.remove('ctrl'); } });
    // Un clic sur l'image met en pause ou relance, comme sur une video. Au
    // toucher, si la barre etait cachee, le premier contact la fait seulement apparaitre.
    var cachee = false;
    cadre.addEventListener('pointerdown', function () { cachee = !demo.classList.contains('ctrl'); });
    cadre.addEventListener('click', function (e) {
      var etaitCachee = cachee;
      cachee = false;
      if (!demo.classList.contains('joue') && !demo.classList.contains('fini')) { return; }
      if (e.target.closest('.demo-barre, .demo-lire')) { return; }
      if (etaitCachee && enLecture) { reveiller(); return; }
      if (enLecture) { pause(); } else { lire(); }
      reveiller();
    });

    // Carte sortie de l'ecran, repliee ou filtree : la voix ne continue pas seule.
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entrees) {
        if (!entrees[0].isIntersecting) { pause(); }
      }).observe(demo);
    }

    afficher();
    var lecteur = { pause: pause };
    lecteurs.push(lecteur);
  });
})();
