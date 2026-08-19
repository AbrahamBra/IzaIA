
/* ================================================================
   IZAIA — script commun à toutes les pages
   ================================================================ */

/* ----------------------------------------------------------------
   PRISE DE RENDEZ-VOUS (Zeeg)
   ----------------------------------------------------------------
   Deux agendas Zeeg DISTINCTS, volontairement :
   - CLIENTS      : les prospects (bouton doré, partout sur le site)
   - PARTENAIRES  : formateurs, commerciaux, builders (bloc « Rejoindre »)
   Séparer les deux vous évite de décrocher sans savoir à qui vous
   parlez, et garde vos statistiques de conversion propres.

   Deux lignes à modifier si un lien change, pas davantage.
   La durée du rendez-vous se configure dans Zeeg, pas ici.
   ---------------------------------------------------------------- */
/* ----------------------------------------------------------------
   FORMULAIRE « Vous préférez écrire ? »
   ----------------------------------------------------------------
   La demande est envoyée à un webhook Make, qui se charge du mail
   vers contact@izaia.fr. Si l'envoi échoue (webhook coupé, réseau,
   bloqueur), on retombe sur l'ouverture du logiciel de messagerie
   du visiteur : aucune demande ne doit être perdue en silence.

   Pour changer de destination, une seule ligne : WEBHOOK.
   ---------------------------------------------------------------- */
var WEBHOOK = 'https://hook.eu1.make.com/szkjs47azlax6k53gse9jl7p5ld2wd4e';
var MAIL_SECOURS = 'contact@izaia.fr';

function envoyerDemandeRappel(e) {
  e.preventDefault();
  var f = e.target;
  var bouton = f.querySelector('button[type="submit"]');
  var etat = f.querySelector('.form-status');

  // Champ piège : s'il est rempli, c'est un robot. On ne dit rien.
  if (f.societe_web && f.societe_web.value) { return; }

  var donnees = {
    nom: f.nom.value,
    tel: f.tel.value,
    email: f.email.value,
    metier: f.metier.options[f.metier.selectedIndex].text,
    message: f.message.value || 'Non précisé',
    page: window.location.href,
    // Date lisible, à l'heure française, plutôt qu'un horodatage UTC.
    date: new Date().toLocaleString('fr-FR', { dateStyle: 'long', timeStyle: 'short' })
  };

  bouton.disabled = true;
  var libelleInitial = bouton.textContent;
  bouton.textContent = 'Envoi…';
  etat.className = 'form-status';
  etat.textContent = '';

  fetch(WEBHOOK, {
    method: 'POST',
    // application/json : Make décompose les champs (nom, tel, email…).
    // Le webhook répond correctement au préflight CORS, c'est donc sans risque.
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(donnees)
  })
    .then(function (r) {
      if (!r.ok) { throw new Error('HTTP ' + r.status); }
      f.reset();
      etat.className = 'form-status ok';
      etat.textContent = 'Demande envoyée. Un expert Izaia vous rappelle sous 24 h ouvrées.';
    })
    .catch(function () {
      // Repli : brouillon de mail prérempli, rien n'est perdu.
      etat.className = 'form-status ko';
      etat.innerHTML = 'L\'envoi automatique a échoué. Votre logiciel de messagerie va s\'ouvrir ' +
        'avec la demande préremplie — sinon, écrivez-nous à <a href="mailto:' + MAIL_SECOURS + '">' +
        MAIL_SECOURS + '</a>.';
      var sujet = encodeURIComponent('Demande de rappel Izaia — ' + donnees.nom);
      var corps = encodeURIComponent(
        'Bonjour,\n\n' +
        'Nom et prénom : ' + donnees.nom + '\n' +
        'Téléphone : ' + donnees.tel + '\n' +
        'Email : ' + donnees.email + '\n' +
        'Métier / secteur : ' + donnees.metier + '\n\n' +
        'Besoin :\n' + donnees.message + '\n\n' +
        'Envoyé depuis izaia.fr'
      );
      window.location.href = 'mailto:' + MAIL_SECOURS + '?subject=' + sujet + '&body=' + corps;
    })
    .then(function () {
      bouton.disabled = false;
      bouton.textContent = libelleInitial;
    });
}

var RDV_CLIENTS     = 'https://zeeg.me/izaia/Rdv-decouverte-Izaia?duration=30';
var RDV_PARTENAIRES = 'https://zeeg.me/izaia/rdv-partenaire-izaia';

/* Identifiants du widget Zeeg : compte, puis créneau de chaque agenda.
   Ils doivent correspondre aux URL ci-dessus. */
var ZEEG_COMPTE = 'izaia';
var ZEEG_CRENEAU = {
  clients: 'Rdv-decouverte-Izaia',
  partenaires: 'rdv-partenaire-izaia'
};

function brancherRdv(selecteur, url, cle, titre) {
  document.querySelectorAll(selecteur).forEach(function (a) {
    // L'attribut href reste renseigné : si le widget ne charge pas,
    // le lien fonctionne normalement et ouvre Zeeg dans un onglet.
    a.href = url;
    a.setAttribute('target', '_blank');
    a.setAttribute('rel', 'noopener');
    a.addEventListener('click', function (e) {
      if (ouvrirRdv(cle, titre)) { e.preventDefault(); }
    });
  });
}

/* ----------------------------------------------------------------
   Fenêtre de prise de rendez-vous
   ----------------------------------------------------------------
   Zeeg ne documente qu'un widget « inline » : on le place donc dans
   une modale maison, ce qui évite au visiteur de quitter le site.
   Si le script Zeeg est bloqué ou indisponible, la fonction renvoie
   false et le clic reprend son comportement normal (nouvel onglet).
   ---------------------------------------------------------------- */
var overlayRdv = null;
var widgetsCharges = {};

function construireOverlay() {
  var o = document.createElement('div');
  o.className = 'rdv-overlay';
  o.setAttribute('role', 'dialog');
  o.setAttribute('aria-modal', 'true');
  o.setAttribute('aria-label', 'Prise de rendez-vous');
  o.innerHTML =
    '<div class="rdv-modale">' +
      '<div class="rdv-tete">' +
        '<span class="rdv-titre"></span>' +
        '<button class="rdv-fermer" type="button" aria-label="Fermer">' +
          '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#122620" stroke-width="2" stroke-linecap="round"><line x1="5" y1="5" x2="19" y2="19"/><line x1="19" y1="5" x2="5" y2="19"/></svg>' +
        '</button>' +
      '</div>' +
      '<div class="rdv-corps"></div>' +
    '</div>';
  document.body.appendChild(o);

  o.querySelector('.rdv-fermer').addEventListener('click', fermerRdv);
  o.addEventListener('click', function (e) { if (e.target === o) { fermerRdv(); } });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && o.classList.contains('ouvert')) { fermerRdv(); }
  });
  return o;
}

function ouvrirRdv(cle, titre) {
  var creneau = ZEEG_CRENEAU[cle];
  if (!creneau) { return false; }

  if (!overlayRdv) { overlayRdv = construireOverlay(); }
  var corps = overlayRdv.querySelector('.rdv-corps');
  overlayRdv.querySelector('.rdv-titre').textContent = titre;

  // Un widget par agenda, construit une seule fois puis réaffiché.
  Object.keys(widgetsCharges).forEach(function (k) {
    widgetsCharges[k].style.display = (k === cle) ? 'block' : 'none';
  });

  if (!widgetsCharges[cle]) {
    var bloc = document.createElement('div');
    var cible = document.createElement('div');
    cible.className = 'zeeg-inline-widget';
    cible.id = 'zeeg-embed-' + ZEEG_COMPTE + '-' + creneau;
    var attente = document.createElement('p');
    attente.className = 'rdv-attente';
    attente.textContent = 'Chargement de l\'agenda…';
    bloc.appendChild(attente);
    bloc.appendChild(cible);
    corps.appendChild(bloc);
    widgetsCharges[cle] = bloc;

    var s = document.createElement('script');
    s.src = 'https://assets.zeeg.me/embed.min.js';
    s.async = true;
    s.setAttribute('data-user', ZEEG_COMPTE);
    s.setAttribute('data-event-type', creneau);
    // Si une redirection est configurée dans Zeeg (plan Professional),
    // elle doit s'appliquer à la page entière et non au seul cadre.
    // Destinations prévues : /merci/ et /merci-partenaire/.
    s.setAttribute('data-redirect-parent', 'true');
    s.onload = function () { attente.remove(); };
    s.onerror = function () {
      // Script inaccessible : on ferme et on laisse l'onglet s'ouvrir.
      fermerRdv();
      window.open(cle === 'partenaires' ? RDV_PARTENAIRES : RDV_CLIENTS, '_blank', 'noopener');
    };
    bloc.appendChild(s);
  }

  overlayRdv.classList.add('ouvert');
  document.body.style.overflow = 'hidden';
  overlayRdv.querySelector('.rdv-fermer').focus();
  return true;
}

function fermerRdv() {
  if (!overlayRdv) { return; }
  overlayRdv.classList.remove('ouvert');
  document.body.style.overflow = '';
}

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
  liens.querySelectorAll('a').forEach(function (a) {
    var li = document.createElement('li');
    var copie = document.createElement('a');
    copie.href = a.getAttribute('href');
    copie.textContent = a.textContent;
    copie.addEventListener('click', fermerMenu);
    li.appendChild(copie);
    liste.appendChild(li);
  });
  panneau.appendChild(liste);

  // Le bouton de RDV porte la classe js-rdv : il sera branché plus bas,
  // en même temps que tous les autres boutons de la page.
  var cta = document.createElement('a');
  cta.className = 'btn btn-gold js-rdv';
  cta.href = RDV_CLIENTS;
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

brancherRdv('a.js-rdv', RDV_CLIENTS, 'clients', 'Rendez-vous téléphonique · sans engagement');
brancherRdv('a.js-rdv-pro', RDV_PARTENAIRES, 'partenaires', 'Rejoindre Izaia · échange partenaires');

/* ----------------------------------------------------------------
   VIDÉO DE PRÉSENTATION
   Lecture au clic. Avec preload="metadata", le navigateur ne charge
   que l'image d'accroche ; les 15,6 Mo ne partent qu'au clic.
   ---------------------------------------------------------------- */
document.querySelectorAll('.vid').forEach(function (box) {
  var cover = box.querySelector('.vid-cover');
  var video = box.querySelector('video');
  if (!cover || !video) return;
  cover.addEventListener('click', function () {
    cover.hidden = true;
    video.preload = 'auto';
    var p = video.play();
    if (p && p.catch) { p.catch(function () { cover.hidden = false; }); }
  });
});

/* ----------------------------------------------------------------
   Maquette : neutraliser l'envoi du formulaire.
   Toutes les pages n'en ont pas — d'où la garde.
   ---------------------------------------------------------------- */
var form = document.querySelector('form');
if (form) {
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    alert('Maquette : formulaire non connecté.');
  });
}

