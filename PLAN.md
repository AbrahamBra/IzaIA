# Plan — Refonte homepage IzaIA (v1 → v2)

## Contexte

Le client a fourni deux documents :
- **PageWeb.pdf** : présentation commerciale IZAIA (contenu de référence)
- **Projet Site V1.docx** : cahier des charges du nouveau site

L'objectif est de refondre `index.html` pour repositionner IzaIA de "formation IA généraliste 2 jours" vers "formation IA pour métiers réglementés et environnements techniques exigeants" (experts-comptables, avocats, banques, industries). Le site reste statique HTML/CSS, sans backend ni framework.

---

## Fichiers à modifier

| Fichier | Changements |
|---|---|
| `index.html` | Refonte majeure — sections nouvelles + mises à jour |
| `expert-comptable/index.html` | Mise à jour taille groupe (8 → 6 à 10) + bios formateurs |
| `styles/common.css` | Ajout CSS pour les nouvelles sections |
| `sitemap.xml` | Mise à jour `lastmod` après modifications |

**Fichiers NON modifiés** : blog articles, mentions-légales, robots.txt, médias.

---

## Plan détaillé — `index.html`

### 1. HERO — Mise à jour du texte

**Localisation actuelle** : lignes 163–198

**Changements** :
- `<h1>` → Nouvelle accroche :
  ```
  Maîtrisez l'intelligence artificielle
  dans votre métier, sans risque
  ```
- `.hero-sub` → Nouveau sous-titre :
  ```
  IZAIA conçoit et dispense des formations en intelligence artificielle dédiées aux métiers réglementés et aux environnements techniques exigeants. Experts-comptables, avocats, banques, industries : nous vous permettons d'intégrer l'IA de manière sécurisée, conforme, structurée et immédiatement opérationnelle.
  ```
- `.hero-proof` items → Remplacer "8 participants max" par "6 à 10 participants"
- Badge : garder "Formation disponible — Financement OPCO possible"
- CTAs : garder "Demander un devis" + "Voir le programme", ajouter un 3e lien "Construire ma formation sur mesure" → `href="#sur-mesure"`

---

### 2. STATS — Mise à jour chiffres

**Localisation actuelle** : lignes 201–222

**Changements** :
- Garder le bloc, mais mettre à jour les labels pour coller au nouveau positionnement :
  - "2 Jours de formation" → garder
  - "8 Ateliers pratiques" → garder
  - "3 Workflows livrés" → garder
  - "100% Terrain, livrables réels" → garder

---

### 3. NOUVELLE SECTION — PROBLÈME (après stats, avant pour-qui)

**ID** : `id="probleme"`

**Structure HTML** :
```html
<section class="section section-alt" id="probleme">
  <div class="container">
    <span class="tag reveal">Pourquoi agir maintenant</span>
    <h2 class="reveal">
      L'IA est déjà utilisée<br>
      <em style="color:var(--accent)">mais sans cadre.</em>
    </h2>
    <p class="reveal" style="...">
      L'intelligence artificielle est déjà utilisée dans la majorité des organisations. Mais :
    </p>
    <!-- 4 cartes problème via .pour-qui-grid existant -->
    <div class="pour-qui-grid">
      <!-- 1 : utilisée sans cadre -->
      <!-- 2 : risques RGPD et confidentialité -->
      <!-- 3 : erreurs liées aux limites des modèles -->
      <!-- 4 : non intégrée dans les processus métier -->
    </div>
  </div>
</section>
```

---

### 4. NOUVELLE SECTION — SOLUTION IZAIA (après problème)

**ID** : `id="solution"`

**Structure** : 3 colonnes (Problème → Solution → Résultats), ou 2 blocs côte à côte.

**Contenu** :
- **Colonne gauche (Solution)** : Approche IZAIA
  - Méthodologie structurée (ACTIF)
  - Cadre de sécurisation des données
  - Cas d'usage métier
  - Automatisations concrètes

- **Colonne droite (Résultats)** : Dès le lendemain
  - Gain de temps
  - Amélioration qualité
  - Sécurisation données
  - Montée en compétence

**CSS** : Utiliser `.pour-qui-grid` ou un nouveau `.solution-grid` (2 colonnes) à ajouter dans `common.css`.

---

### 5. NOUVELLE SECTION — NOTRE APPROCHE (après solution)

**ID** : `id="approche"`

**Contenu** : 4 points clés en grille 2×2 ou ligne de 4 icônes
- Présentiel uniquement
- Groupes de 6 à 10 personnes
- Ateliers pratiques
- Application immédiate

**CSS** : Réutiliser `.stats-grid` ou `.pour-qui-grid` adapté.

---

### 6. Section POUR QUI — Mise à jour ciblage

**Localisation actuelle** : lignes 225–255

**Changements** :
- Sous-titre → mentionner métiers réglementés (données sensibles, conformité)
- 3 cards → garder la structure, adapter les textes pour inclure les métiers réglementés dans les exemples
- Card 1 : "Vous travaillez avec des données sensibles" (avocats, comptables, banques…)
- Card 2 : garder (réponses manuelles)
- Card 3 : garder (comprendre l'IA pour de vrai)

---

### 7. Section PROGRAMME — Mise à jour groupe

**Localisation actuelle** : lignes 258–444

**Changements** :
- `.meta-pill` "👥 8 participants max" → "👥 6 à 10 participants" (2 occurrences : Jour 1 et Jour 2)

---

### 8. NOUVELLE SECTION — FORMATION SUR MESURE (après programme)

**ID** : `id="sur-mesure"`

**Structure** :
```html
<section class="section section-alt" id="sur-mesure">
  <div class="container">
    <span class="tag reveal">Formation sur mesure</span>
    <h2 class="reveal">
      Votre métier est unique.<br>
      <em style="color:var(--accent)">Votre formation aussi.</em>
    </h2>
    <p class="reveal" style="...">
      Sans aucun coût supplémentaire. Nos ingénieurs IA analysent vos workflows,
      contraintes réglementaires et construisent une formation dédiée.
    </p>
    <!-- 2 cartes exemples sectoriels -->
    <div class="exemples-grid"> <!-- nouveau CSS -->
      <!-- Exemple 1 : Industrie textile technique -->
      <!-- Exemple 2 : Négoce de produits chimiques -->
    </div>
    <!-- CTA -->
    <div style="text-align:center; margin-top:3rem">
      <a href="#contact" class="btn btn-primary">Construire ma formation sur mesure</a>
    </div>
  </div>
</section>
```

**Contenu Exemple 1 — Industrie textile technique** :
- Profils : opérateurs, techniciens, ingénieurs, responsables production, commerciaux, fonctions support
- Thèmes : veille normative, confidentialité, Mistral AI (français), REACH, cahiers des charges aéronautiques, traçabilité matières

**Contenu Exemple 2 — Négoce de produits chimiques** :
- Problème : demandes complexes multi-critères, dépendance experts internes, délais urgents
- Thèmes : FDS, conformité, base de connaissance, RGPD, confidentialité, précision

**CSS à ajouter dans `common.css`** :
```css
.exemples-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-top: 2.5rem;
}
.exemple-card {
  background: var(--cream);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 2rem;
}
.exemple-card-sector {
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 0.75rem;
}
@media (max-width: 640px) {
  .exemples-grid { grid-template-columns: 1fr; }
}
```

---

### 9. Section FORMATEURS — Mise à jour bios et rôles

**Localisation actuelle** : lignes 481–561

**Changements Abraham Brakha** :
- `.formateur-role` : "Formateur" → "Co-Fondateur — IZAIA / NGM Immersion"
- `.formateur-title` : "Head of Growth & IA · Co-fondateur ChallengersLab" → "Expert en intelligence artificielle & ingénierie des systèmes"
- `.formateur-bio` → Nouvelle bio :
  ```
  Abraham Brakha est spécialisé dans la conception et l'intégration de solutions d'intelligence artificielle en environnement professionnel. Il intervient sur la structuration des workflows, l'automatisation des tâches à forte volumétrie et la mise en place de systèmes IA sécurisés. Au sein d'IZAIA, il conçoit des cas d'usage concrets permettant une application immédiate en situation de travail.
  ```
- Tags : "Make & n8n", "Automatisation", "IA générative", "Ingénierie systèmes"

**Changements Céline Rinaudo** :
- `.formateur-role` : "Formatrice" → "Responsable administrative & conformité formation"
- `.formateur-title` : "DRH · 23 ans d'expérience en Ressources Humaines" → "Form'H · Conformité Qualiopi & OPCO"
- `.formateur-bio` → Nouvelle bio :
  ```
  Céline Rinaudo est spécialisée dans la structuration et la gestion des dispositifs de formation professionnelle. Elle accompagne les entreprises et organismes de formation sur les enjeux de conformité Qualiopi, ingénierie administrative et financement via les OPCO. Au sein d'IZAIA, elle assure l'ensemble de la gestion administrative des formations : montage des dossiers, suivi des prises en charge, conformité réglementaire et relations avec les financeurs.
  ```
- Tags : "Conformité Qualiopi", "OPCO", "Financement formation", "Administratif"

---

### 10. NOUVELLE SOUS-SECTION — RÉFÉRENTS MÉTIER (après les 3 formateurs)

**Structure** : Séparateur visuel + titre + 2 cartes

```html
<!-- Dans la section #formateurs, après .formateurs-grid -->
<div class="referents-header reveal" style="margin-top:4rem; margin-bottom:2rem; text-align:center">
  <span class="tag">Référents métier</span>
  <h3 style="font-size:1.5rem; margin-top:0.75rem">
    Une expertise sectorielle intégrée
  </h3>
  <p style="color:var(--muted); max-width:54ch; margin:0.5rem auto 0">
    IZAIA s'appuie sur des référents métier garantissant l'adéquation des formations avec les exigences spécifiques de chaque profession.
  </p>
</div>
<div class="referents-grid reveal"> <!-- nouveau CSS : 2 colonnes -->
  <!-- Raphaël Garcin -->
  <!-- Maître Mouchtouris -->
</div>
```

**Contenu Raphaël Garcin** :
- Rôle : Expert-comptable — Cabinet COFIRECO
- Adresse : 11, cours Aristide Briand — 69300 Caluire-et-Cuire
- Email : cabinet@cofireco.net
- Tél : 04 78 23 26 81
- Bio : "Accompagne depuis plus de 20 ans les entreprises dans leur gestion financière, comptable et fiscale. Il garantit l'intégration des outils d'IA dans le respect des obligations réglementaires du secteur comptable (RGPD, normes ordinales, confidentialité)."
- Tags : "Expert-comptable", "Commissaire aux comptes", "RGPD comptable"

**Contenu Maître Emmanuel Mouchtouris** :
- Rôle : Avocat associé & dirigeant — Saint Cyr Avocats, Lyon
- Adresse : 21 avenue du Maréchal de Saxe, 69006 Lyon
- Email : em@saintcyravocats.com
- Tél : 04 78 47 87 45
- Bio : "Avocat au barreau de Lyon depuis 1994. Intervient en contentieux commercial, droit du travail et propriété intellectuelle. Apporte à IZAIA une expertise essentielle sur les enjeux de secret professionnel, déontologie et sécurité des données juridiques."
- Tags : "Droit des affaires", "Secret professionnel", "Données juridiques"

**CSS à ajouter** :
```css
.referents-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-top: 1.5rem;
}
.referent-card {
  background: var(--cream);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.75rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.referent-role {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--accent);
}
.referent-name {
  font-family: 'Instrument Serif', serif;
  font-size: 1.25rem;
}
.referent-contact {
  font-size: 0.82rem;
  color: var(--muted);
  line-height: 1.8;
}
@media (max-width: 640px) {
  .referents-grid { grid-template-columns: 1fr; }
}
```

---

### 11. NOUVELLE SECTION — POSITIONNEMENT (après formateurs/référents)

**ID** : `id="positionnement"`

```html
<section class="section section-alt" id="positionnement">
  <div class="container" style="text-align:center; max-width:760px">
    <span class="tag reveal">Notre positionnement</span>
    <h2 class="reveal">
      Une double expertise :<br>
      <em style="color:var(--accent)">métier + intelligence artificielle.</em>
    </h2>
    <p class="reveal" style="color:var(--muted); font-size:1.05rem; max-width:54ch; margin:1rem auto 2.5rem; line-height:1.75;">
      IZAIA ne repose pas uniquement sur des spécialistes de l'IA.
      Nous réunissons experts techniques, professionnels métier et intervenants terrain.
    </p>
    <!-- Encart citation -->
    <blockquote class="reveal" style="...">
      "Ce n'est pas l'IA qui fait la différence.
       C'est la manière dont elle est utilisée dans votre métier."
    </blockquote>
    <!-- 3 piliers -->
    <div class="pour-qui-grid" style="margin-top:2rem; text-align:left">
      <!-- Experts techniques -->
      <!-- Professionnels métier -->
      <!-- Intervenants terrain -->
    </div>
  </div>
</section>
```

---

### 12. Section TARIF — Mise à jour groupe

**Localisation actuelle** : lignes 577–648

**Changements** :
- "Jusqu'à 8 participants" → "6 à 10 participants" (dans chaque `.tarif-features`)

---

### 13. Navigation — Ajout lien "Sur mesure"

**Localisation actuelle** : lignes 128–160

**Changements** :
- Ajouter `<li><a href="#sur-mesure">Sur mesure</a></li>` dans `nav-links`
- Ajouter le même lien dans le menu mobile `#mobileMenu`

---

### 14. Section CONTACT — Mise à jour téléphone

**Localisation actuelle** : lignes 651–734

**Changements** :
- Ajouter le numéro de téléphone Alain : **+33 6 07 09 70 70**
  ```html
  <li class="reveal">
    <span class="contact-icon">📞</span>
    <div>
      <strong>Téléphone</strong>
      <span><a href="tel:+33607097070">+33 6 07 09 70 70</a></span>
    </div>
  </li>
  ```

---

### 15. FOOTER — Mise à jour

**Localisation actuelle** : lignes 816–850

**Changements** :
- Ajouter lien "Sur mesure" dans la navigation footer
- SIREN : déjà présent (93441887200016) — vérifier cohérence avec DOCX (SIREN 934 418 872 = même numéro tronqué)

---

## Plan détaillé — `expert-comptable/index.html`

**Changements mineurs** :
1. `.meta-pill` "👥 8 participants max" → "👥 6 à 10 participants" (2 occurrences)
2. Mise à jour bio Abraham Brakha (même texte que index.html)
3. Mise à jour bio Céline Rinaudo (même texte que index.html)
4. Tagline `.formateur-role` pour Abraham : "Co-Fondateur — IZAIA / NGM Immersion"
5. Tagline `.formateur-role` pour Céline : "Responsable administrative & conformité formation"

---

## Plan détaillé — `styles/common.css`

**Ajouts en fin de fichier** :
```css
/* ── Exemples sectoriels (section sur mesure) */
.exemples-grid { ... }
.exemple-card { ... }
.exemple-card-sector { ... }

/* ── Référents métier */
.referents-grid { ... }
.referent-card { ... }
.referent-role { ... }
.referent-name { ... }
.referent-contact { ... }

/* ── Responsive pour les nouvelles grilles */
@media (max-width: 640px) {
  .exemples-grid, .referents-grid { grid-template-columns: 1fr; }
}
```

---

## Plan détaillé — `sitemap.xml`

Mettre à jour `<lastmod>` de `index.html` et `expert-comptable/index.html` à la date du jour (2026-05-05).

---

## Ordre d'exécution recommandé

1. `styles/common.css` — ajouter les nouveaux composants CSS
2. `index.html` — appliquer toutes les modifications dans l'ordre du document
3. `expert-comptable/index.html` — modifications mineures
4. `sitemap.xml` — mise à jour des dates
5. `git add` + `git commit` + `git push origin main`

---

## Vérification

- Ouvrir `index.html` dans un navigateur localement
- Vérifier l'ordre des sections dans la page
- Tester le menu mobile (hamburger) — vérifier que "Sur mesure" est bien présent
- Vérifier que les liens `href="#sur-mesure"` fonctionnent (scroll vers la section)
- Vérifier le responsive sur mobile (640px) : les grilles `.exemples-grid` et `.referents-grid` passent en 1 colonne
- Vérifier la cohérence des tailles de groupe (6 à 10) dans toutes les sections : hero, programme (meta-pill), tarif (features)
- Valider le lien "Construire ma formation sur mesure" → `#sur-mesure`
- S'assurer que les bios Abraham et Céline sont cohérentes entre `index.html` et `expert-comptable/index.html`
