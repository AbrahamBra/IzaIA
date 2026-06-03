# Refonte IzaIA — Récap de conception

> Session des 2–3 juin 2026. Document de reprise : tout ce qui a été décidé ensemble, pour continuer un autre jour.

## Le pivot
IzaIA passe d'un organisme de formation IA à **deux pôles réunis sous une même marque** :
- **Cabinet de développement IA** (conseil + construction d'outils IA sur mesure)
- **Organisme de formation IA**

Positionnement élargi : **on ne se positionne plus uniquement sur le réglementé**. Cible = toutes les organisations, tous secteurs. Les professions réglementées (avocats, experts-comptables…) deviennent des **exemples parmi d'autres**, plus *le* positionnement.

---

## Décisions verrouillées

### 1. Architecture du site
**Hub à deux portes** : une seule marque IzaIA, une home-carrefour qui ouvre sur les deux pôles à parité. Chaque pôle aura son espace (`/formation/`, `/conseil/`). Les pages métier existantes gardent leurs URLs (SEO préservé).

### 2. Charte graphique (reprise de `styles/common.css`)
- Fond **crème `#FDFAF6`** (jamais sombre), texte encre `#1C1917`, gris `#78716C`
- **Accent unique : terracotta `#C2410C`** — PAS de vert (le vert testé a été abandonné, hors-charte)
- Titres **Instrument Serif** (poids 400, le `em` passe en terracotta), corps **Inter**
- Boutons **pilule** (radius 50px), cartes radius 16px, ombres douces, tags sobres avec petit tiret
- **Zéro emoji.** Sobre, pro, niveau dirigeant.

### 3. Voix éditoriale (standard pour tout le site)
- **« nous » / « vous »**, jamais « on » (tic IA à bannir)
- **Co-construction** : « ensemble », « avec vous », « à votre rythme », « à vos côtés »
- **Bénéfice avant fonctionnalité**
- **Pas de tirets cadratins** (virgules)
- Phrase-patron de référence : *« Après l'audit, nous concevons ensemble votre feuille de route IA, en respectant vos priorités. »*

### 4. Hero de la home — option « 3 » verrouillée
Mise en page miroir, sobre :
- **« IA »** en grand, terracotta, en haut (signature)
- **Filet vertical** au centre, deux pôles de part et d'autre :
  - Gauche : **Cabinet de développement** → bouton *Découvrir le cabinet*
  - Droite : **Organisme de formation** → bouton *Voir les formations*
- Chaque bouton **sous son pôle** (cohérence)
- **Pas** de stats, d'eyebrow, de sous-titre ni de carte « livrables » dans le hero
- ⏳ *En attente* : faut-il inverser le hero pour mettre Formation à gauche (cohérence avec les cartes) ? Le titre de marque reste « Cabinet de développement IA et organisme de formation IA » (cabinet d'abord).

### 5. Section « Découvrez IzaIA » (tag « Nos deux pôles », sans narratif « maison »)
Deux cartes. **Formation à gauche/en premier.**

#### Carte Formation
- Titre : **« Formation pensée pour votre métier »**
- Généraliste **supprimé** : 100% métier/sur-mesure
- Intro : *« Votre métier a ses spécificités, techniques ou réglementaires. Nous concevons gratuitement, avec vous, le programme de formation qui s'y adapte, sur une ou deux journées, en présentiel et sur vos cas réels. »*
- **Déjà conçus pour** (liens vers pages préparées) : Expert-comptable · Banque · Immobilier · Négoce de produits chimiques · Avocat · Textiles techniques
- CTA : **« Échangeons sur votre programme sur mesure »** + sous-texte *« Gratuit et sans engagement »* (mène au formulaire de contact)
- Bulle **OPCO** : *« Une formation finançable par votre OPCO : nous montons le dossier de prise en charge avec vous. »*
- Lien : **« Voir le détail de nos formations → »** (uniquement vers la page Formation)

#### Carte Conseil & Développement
- Titre : **« Adaptez votre organisation à l'IA »** (bénéfice ; « organisation » plutôt qu'« entreprise »)
- Intro : *« De la stratégie aux outils, nous intégrons l'IA dans votre organisation, avec vos équipes et à votre rythme. »*
- 4 services :
  - **Conseil & cadrage** — après l'audit, nous concevons ensemble votre feuille de route IA, en respectant vos priorités.
  - **Automatisation** — vos tâches répétitives, repérées avec vous et passées en pilote automatique.
  - **Développement** — des outils sur mesure (assistants, agents, applications internes), pensés avec vous pour votre métier.
  - **Suivi & support** — nous restons à vos côtés : support, maintenance et évolution sur toute la durée du contrat.
- Bulle **Trésorerie** : *« Un paiement mensualisé qui préserve votre trésorerie : vous avancez sur l'IA sans immobiliser votre cash. »*
- Lien : **« Découvrir le cabinet → »**

### 6. Bridge (bas de home)
*« Les mêmes experts vous forment **et** construisent vos outils. Nous ne livrons pas une boîte noire : nous rendons vos équipes autonomes. »*

---

## Pôle Conseil — éléments validés (à remettre sur charte + voix lors de la page `/conseil/`)
*Ces blocs ont été travaillés en maquette « démo » avant le passage à la charte. À re-rendre sur fond crème/terracotta et à repasser dans la voix nous/vous.*
- **Hero cabinet** : *« Vos équipes, augmentées par l'IA. Sans bouleverser leur façon de travailler. »* + sous-titre avec exemples (e-mails triés et pré-rédigés, devis prêts en quelques secondes, toutes les données utiles à un dossier) + **bulle** : « 📚 Dans vos données : la bonne réponse au milieu de milliers de documents internes / 🌐 Sur internet : les informations **spécifiques** pour compléter un dossier ». Termine par « IzaIA les conçoit et forme vos collaborateurs, jusqu'à l'autonomie. »
- **Section Trésorerie** : accroche *« Votre trésorerie est précieuse. Conservez-la. »* → contrat global (réflexion + conception + formation + suivi), facturé en mensualités. Bloc « Suivi » = **maintenance, support et évolution sur toute la durée du contrat**. (Le bloc CSM/adoption a été retiré.)
- **Méthode** : Audit → Cadrage → Prototype → Développement → Adoption.
- **Contact unique** pour les deux pôles, avec sélecteur « Je viens pour : une formation / un projet conseil & développement ».
- **Cible** : large (toutes organisations, tous secteurs).

---

## Maquettes — où reprendre
Compagnon visuel (fichiers HTML persistés) :
`C:\Users\Abraham\IzaIa\.superpowers\brainstorm\458-1780480601\content\`
- **Home finale (référence)** : `home-charte-v8.html` (hero option 3 + 2 cartes sur charte)
- Hero retenu : `hero-A-3.html` (option 3)
- Étapes intermédiaires conservées (architectures, services conseil, trésorerie, etc.)

Pour relancer le serveur du compagnon un autre jour :
`bash "/c/Users/Abraham/.claude/skills/brainstorming/scripts/start-server.sh" --project-dir "/c/Users/Abraham/IzaIa"`

---

## Reste à faire (prochaine session)
1. **Page `/conseil/`** complète sur charte + voix (hero augmenté, 4 services, méthode, trésorerie, contact).
2. **Page `/formation/`** : le détail (programmes, déroulé, formats 1–2 j, pages métier).
3. **Navigation globale** : menus déroulants `Formation ▾` / `Conseil & Dév ▾`.
4. **Preuve / étude de cas** du cabinet : choisir un projet réel à raconter (ex. On Medical en santé, immobilier…), décider de **citer le client ou rester anonyme**.
5. **Trancher** : inverser le hero (Formation à gauche) ? ; harmoniser « entreprise » vs « organisation ».
6. **Implémentation** : porter le tout dans le vrai site (HTML/CSS sur `common.css`), mettre à jour les pages existantes, sitemap, et déployer.

---
*Décisions prises en mode brainstorming visuel. Aucune modification du site de production n'a encore été faite — tout est en maquette.*
