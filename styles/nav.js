/* ═══════════════════════════════════════════════════════════════
   NAVIGATION — panneau mobile
   ═══════════════════════════════════════════════════════════════
   Source unique. Ce code existait en double, inline dans l'accueil
   et dans izaia-2026.js ; l'unifier evitait d'en creer une
   troisieme copie en l'apportant aux pages heritees.

   Sous 1024 px la barre est masquee au profit du bouton hamburger.
   Le panneau reprend les entrees du menu ; celle qui deploie les
   treize verticales y est repliee, sinon elle noie le panneau sous
   vingt entrees et repousse Contact hors d'atteinte.
   ═══════════════════════════════════════════════════════════════ */
/* ----------------------------------------------------------------
   MENU MOBILE
   ----------------------------------------------------------------
   Sous 1024 px, la barre de navigation est masquée au profit du
   bouton hamburger. Le panneau ci-dessous reprend les mêmes liens,
   plus le bouton de prise de rendez-vous.
   ---------------------------------------------------------------- */
(function () {
  var burger = document.querySelector('.burger');
  var liens = document.querySelector('.nav-links');
  var entete = document.querySelector('header.site');
  if (!burger || !liens || !entete) { return; }

  var panneau = document.createElement('div');
  panneau.className = 'nav-panneau';
  panneau.id = 'menu-mobile';

  var liste = document.createElement('ul');
  // Une entrée du menu déploie les treize verticales. Recopiée à plat, elle
  // noyait le panneau mobile sous vingt entrées et repoussait Contact et le
  // bouton de rendez-vous hors d'atteinte. Elle est donc repliée par défaut,
  // et s'ouvre d'une pression.
  liens.querySelectorAll(':scope > li').forEach(function (source) {
    var lien = source.querySelector(':scope > a');
    if (!lien) { return; }
    var enfants = source.querySelectorAll('.nav-drop a');
    var li = document.createElement('li');

    if (enfants.length > 2) {
      var bouton = document.createElement('button');
      bouton.type = 'button';
      bouton.className = 'mm-deplier';
      bouton.textContent = lien.textContent.trim();
      bouton.setAttribute('aria-expanded', 'false');

      var sous = document.createElement('ul');
      sous.className = 'mm-sous';
      sous.hidden = true;

      // Le bouton remplace un lien : sans cette première entrée, la page de
      // regroupement deviendrait inatteignable sur téléphone.
      var entrees = [{ href: lien.getAttribute('href'), texte: 'Toutes les formations' }];
      enfants.forEach(function (a) {
        entrees.push({ href: a.getAttribute('href'), texte: a.textContent });
      });
      entrees.forEach(function (e) {
        var sli = document.createElement('li');
        var copie = document.createElement('a');
        copie.href = e.href;
        copie.textContent = e.texte;
        copie.addEventListener('click', fermerMenu);
        sli.appendChild(copie);
        sous.appendChild(sli);
      });

      bouton.addEventListener('click', function () {
        var ouvert = bouton.getAttribute('aria-expanded') === 'true';
        bouton.setAttribute('aria-expanded', String(!ouvert));
        sous.hidden = ouvert;
      });

      li.appendChild(bouton);
      li.appendChild(sous);
    } else {
      var simple = document.createElement('a');
      simple.href = lien.getAttribute('href');
      simple.textContent = lien.textContent.trim();
      simple.addEventListener('click', fermerMenu);
      li.appendChild(simple);
    }
    liste.appendChild(li);
  });
  panneau.appendChild(liste);

  // Le bouton de RDV porte la classe js-rdv : il sera branché plus bas,
  // en même temps que tous les autres boutons de la page.
  var cta = document.createElement('a');
  cta.className = 'btn btn-gold js-rdv';
  /* Les pages heritees ne definissent pas RDV_CLIENTS : on retombe sur
     l'adresse de l'agenda plutot que de laisser un lien vide. */
  cta.href = (typeof RDV_CLIENTS !== 'undefined')
    ? RDV_CLIENTS
    : 'https://zeeg.me/izaia/Rdv-decouverte-Izaia?duration=30';
  cta.textContent = 'RDV téléphonique sans engagement';
  cta.addEventListener('click', fermerMenu);
  panneau.appendChild(cta);

  document.body.appendChild(panneau);

  burger.setAttribute('aria-expanded', 'false');
  burger.setAttribute('aria-controls', 'menu-mobile');

  function placer() {
    panneau.style.top = Math.round(entete.getBoundingClientRect().bottom) + 'px';
  }
  function ouvrirMenu() {
    placer();
    panneau.classList.add('ouvert');
    document.body.classList.add('menu-ouvert');
    burger.setAttribute('aria-expanded', 'true');
    burger.setAttribute('aria-label', 'Fermer le menu');
  }
  function fermerMenu() {
    panneau.classList.remove('ouvert');
    document.body.classList.remove('menu-ouvert');
    burger.setAttribute('aria-expanded', 'false');
    burger.setAttribute('aria-label', 'Ouvrir le menu');
  }

  burger.addEventListener('click', function () {
    if (panneau.classList.contains('ouvert')) { fermerMenu(); } else { ouvrirMenu(); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { fermerMenu(); }
  });
  // Retour au format bureau : le panneau n'a plus lieu d'être.
  window.addEventListener('resize', function () {
    if (window.innerWidth > 1024) { fermerMenu(); } else { placer(); }
  });
})();
