/* Navigation dans la page : sommaire collant et filtres d'exemples.
   Sans ce script, le sommaire et les pastilles restent des liens d'ancre. */
(function () {
  var racine = document.documentElement;
  var entete = document.querySelector('header.site');
  var sommaire = document.querySelector('.sommaire');
  if (!entete || !sommaire) return;

  // Le sommaire se colle sous l'en-tete, dont la hauteur varie avec la largeur.
  function mesurer() {
    racine.style.setProperty('--entete', entete.offsetHeight + 'px');
  }
  mesurer();
  window.addEventListener('resize', mesurer);

  // Rubrique en cours : la derniere section passee sous l'en-tete.
  var liens = Array.prototype.slice.call(sommaire.querySelectorAll('a'));
  var cibles = liens.map(function (a) {
    return document.getElementById(a.getAttribute('href').slice(1));
  });
  var liste = sommaire.querySelector('ul');
  var courant = -1;
  function reperer() {
    var seuil = entete.offsetHeight + sommaire.offsetHeight + 24;
    var trouve = -1;
    cibles.forEach(function (c, i) {
      if (c && c.getBoundingClientRect().top <= seuil) trouve = i;
    });
    if (trouve === courant) return;
    courant = trouve;
    liens.forEach(function (a, i) {
      if (i === courant) a.setAttribute('aria-current', 'true');
      else a.removeAttribute('aria-current');
    });
    // Sur telephone le sommaire defile : garder la rubrique en cours visible.
    if (courant >= 0) {
      var a = liens[courant];
      var gauche = a.offsetLeft - liste.offsetLeft;
      if (gauche < liste.scrollLeft || gauche + a.offsetWidth > liste.scrollLeft + liste.clientWidth) {
        liste.scrollLeft = Math.max(0, gauche - 24);
      }
    }
  }
  window.addEventListener('scroll', reperer, { passive: true });
  window.addEventListener('resize', reperer);
  reperer();

  // Sur telephone, les cartes d'exemples se replient sur leur titre. La premiere
  // reste ouverte pour montrer ce qu'il y a derriere. Le HTML les livre ouvertes.
  var cartes = Array.prototype.slice.call(document.querySelectorAll('details.exemple'));
  var etroit = window.matchMedia('(max-width: 699px)');
  function plier() {
    cartes.forEach(function (d, i) {
      // Ecran large : tout est ouvert, et les titres ne sont plus cliquables.
      if (!etroit.matches || i === 0) d.setAttribute('open', '');
      else d.removeAttribute('open');
    });
  }
  if (cartes.length) {
    var etaitEtroit = etroit.matches;
    if (etaitEtroit) plier();
    // Rotation du telephone ou fenetre redimensionnee : on ne replie ou ne
    // rouvre qu'au franchissement du seuil, pas a chaque redimensionnement.
    window.addEventListener('resize', function () {
      if (etroit.matches !== etaitEtroit) { etaitEtroit = etroit.matches; plier(); }
    });
  }

  // Filtres d'exemples : une famille a la fois, ou toutes.
  var barre = document.querySelector('.filtres');
  if (!barre) return;
  var pastilles = Array.prototype.slice.call(barre.querySelectorAll('a'));
  var blocs = Array.prototype.slice.call(document.querySelectorAll('.famille-bloc'));
  barre.setAttribute('role', 'group');
  barre.classList.add('actifs');
  function filtrer(cle) {
    blocs.forEach(function (b) {
      b.hidden = cle !== 'tous' && b.getAttribute('data-famille') !== cle;
    });
    pastilles.forEach(function (p) {
      p.setAttribute('aria-pressed', p.getAttribute('data-filtre') === cle ? 'true' : 'false');
    });
  }
  pastilles.forEach(function (p) {
    p.setAttribute('role', 'button');
    p.addEventListener('click', function (e) {
      e.preventDefault();
      filtrer(p.getAttribute('data-filtre'));
      // Si la barre est sortie de l'ecran, y revenir : la page vient de raccourcir.
      if (barre.getBoundingClientRect().top < entete.offsetHeight + sommaire.offsetHeight) {
        barre.scrollIntoView();
      }
    });
    p.addEventListener('keydown', function (e) {
      if (e.key === ' ') { e.preventDefault(); p.click(); }
    });
  });
  // Un lien direct vers une famille masquee la fait reapparaitre.
  window.addEventListener('hashchange', function () {
    var cible = document.getElementById(location.hash.slice(1));
    var bloc = cible && cible.closest('.famille-bloc');
    if (bloc && bloc.hidden) { filtrer('tous'); cible.scrollIntoView(); }
  });
})();
