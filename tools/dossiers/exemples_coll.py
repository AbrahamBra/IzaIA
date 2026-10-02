# -*- coding: utf-8 -*-
"""Les quinze exemples d'outils de la page /collectivites/agents-ia/.

Dans une collectivite, « agent » designe une personne : les cartes disent
« l'agent IA » pour la machine et « l'agent municipal » pour celui qui relit.

    python tools/dossiers/exemples_coll.py   # regenere la section dans coll-agents-corps.html
    python tools/dossiers/assembler.py coll-agents

Regle d'ecriture : voir cartes.greffer. Faisabilite de chaque exemple :
docs/superpowers/notes/2026-10-01-faisabilite-agents.md. L'exemple « pieces d'un
dossier d'urbanisme » a ete retire le 2026-10-01 : acces au logiciel
d'instruction incertain, enjeu contentieux, aucun retour d'experience.
"""
import cartes

# (ancre, titre de famille, [(titre, aujourd'hui, l'outil, l'agent[, a savoir])])
FAMILLES = [
    ("assemblees", "Les assemblées et les actes", [
        ("Le procès-verbal de séance du conseil",
         "Le procès-verbal se rédige après chaque séance, à partir de notes et de l'enregistrement, qu'il faut réécouter par passages.",
         "Il transcrit l'enregistrement de la séance et prépare un projet de procès-verbal dans la trame de la collectivité, avec les points à l'ordre du jour, les interventions et les votes.",
         "Il vérifie les votes, les noms et les chiffres, avant que le conseil n'arrête le procès-verbal à la séance suivante.",
         "Des produits prêts à l'emploi font déjà cette transcription. Nous les comparons avec vous avant de construire un agent IA."),
        ("Le projet de délibération",
         "Chaque projet repart d'une délibération précédente, reprise à la main, des visas au dispositif.",
         "Il prépare le projet de délibération à partir des modèles de la collectivité et des éléments transmis par le service.",
         "Il vérifie les visas et la compétence du conseil, corrige le texte, puis le transmet à l'élu qui le rapporte."),
        ("Le projet d'arrêté",
         "Circulation, occupation du domaine public, voirie : les mêmes arrêtés reviennent, avec des mentions obligatoires qu'il ne faut pas oublier.",
         "Il prépare le projet d'arrêté à partir du modèle de la collectivité et de la demande reçue.",
         "Il vérifie les dates, les lieux et le fondement juridique, puis présente le projet à la signature de l'autorité compétente."),
        ("La note de synthèse pour les élus",
         "Avant chaque séance, un agent municipal résume les rapports des services pour les élus, souvent au dernier moment.",
         "Il prépare une note courte pour chaque rapport : l'objet, les montants en jeu, la décision demandée.",
         "Il relit chaque note en ouvrant le rapport d'origine, parce qu'une synthèse plausible n'est pas toujours exacte."),
    ]),
    ("accueil", "L'accueil et l'information des administrés", [
        ("Le tri des demandes entrantes",
         "Courriels et formulaires du site arrivent dans la même messagerie. Un agent municipal les lit un par un pour les transmettre au bon service.",
         "Il lit chaque demande écrite, en identifie l'objet et propose le service destinataire. Il n'est pas relié aux messageries du centre communal d'action sociale.",
         "Il confirme ou corrige l'orientation proposée.",
         "Si une demande sociale arrive dans la messagerie générale, l'agent IA l'oriente vers le service sans préparer de réponse. Des logiciels de gestion de la relation avec les administrés font déjà ce tri."),
        ("La réponse de premier niveau",
         "Horaires, pièces à fournir, démarches en ligne : beaucoup de demandes appellent la même réponse, réécrite à chaque fois.",
         "Il prépare un brouillon de réponse à partir des informations que la collectivité a validées et publiées.",
         "Il relit, adapte et envoie. Aucune réponse ne part sans lui."),
        ("Le suivi des demandes sans réponse",
         "Une demande restée sans réponse se remarque le jour où l'administré relance.",
         "Il tient la liste des demandes en attente dans la messagerie ou le logiciel où elles arrivent, par service et par ancienneté. Il signale celles qui approchent du délai que la collectivité s'est fixé.",
         "Il transmet la liste au responsable du service, qui décide quoi répondre.",
         "L'agent IA ne voit pas les demandes faites au guichet ou par téléphone, tant qu'elles n'ont pas été saisies."),
        ("Le classement des signalements de voirie",
         "Nid-de-poule, éclairage en panne, dépôt sauvage : les signalements arrivent par téléphone, par courriel et par le site, chacun décrit à sa façon.",
         "Il classe les signalements écrits par nature et par secteur, repère les doublons probables et prépare la fiche pour les services techniques.",
         "Il saisit les signalements reçus par téléphone, valide chaque fiche et fixe la priorité."),
        ("L'information municipale sur plusieurs supports",
         "Une même information doit paraître sur le site, sur les réseaux sociaux et à l'affichage. Elle se réécrit trois fois.",
         "Il prépare les trois versions à partir d'une seule note, en adaptant la longueur et le ton à chaque support.",
         "Il vérifie les dates, les lieux et les noms cités, puis publie."),
    ]),
    ("finances", "Les finances, les subventions et les marchés", [
        ("Le dossier de demande de subvention",
         "Chaque financeur a son règlement, son formulaire et ses pièces. Pour monter le dossier, il faut relire le règlement ligne à ligne.",
         "Il relève dans le règlement les conditions d'éligibilité, les pièces exigées et les dates, puis prépare une première rédaction à partir des éléments de l'opération à financer.",
         "Il vérifie chaque condition dans le règlement d'origine, et il arrête lui-même les montants et le plan de financement."),
        ("La veille des appels à projets",
         "Les appels à projets de l'État, de la région et du département paraissent sur des sites différents. Certains sont repérés trop tard.",
         "Il relève les nouveaux appels à projets et signale ceux qui correspondent aux opérations que la collectivité lui a indiquées.",
         "Il lit le texte de l'appel à projets avant d'en parler à la direction.",
         "La plateforme publique Aides-territoires recense déjà ces aides, avec leurs critères. L'agent IA part de cette base et fait le tri selon vos opérations."),
        ("La trame du cahier des charges",
         "Le cahier des charges d'un nouveau marché repart de celui d'un marché précédent, adapté à la main.",
         "Il prépare une trame à partir des marchés déjà passés par la collectivité et de la description du besoin. Il n'analyse ni ne note aucune offre.",
         "Il définit lui-même le besoin et les critères, puis complète la trame."),
    ]),
    ("memoire", "Les documents et la mémoire de la collectivité", [
        ("La recherche dans les délibérations et les arrêtés",
         "Pour retrouver ce que le conseil a voté sur un sujet il y a six ans, il faut savoir où chercher, ou demander à celui qui s'en souvient.",
         "Il répond en langage courant à partir des délibérations, des arrêtés et du règlement du plan local d'urbanisme, et il cite l'acte d'où vient chaque réponse.",
         "Il ouvre l'acte cité avant de s'en servir.",
         "L'agent IA ne dit pas dans quelle zone se trouve une parcelle."),
        ("Les réponses sur les procédures internes",
         "Les procédures tiennent dans des notes dispersées et dans la mémoire des agents en poste. Chaque départ en emporte une partie.",
         "Il répond aux questions des agents municipaux à partir des procédures écrites que la collectivité a versées dans sa base, et il cite le document d'origine.",
         "Il vérifie la réponse dans le document cité, et signale au responsable du service une procédure qui n'est plus à jour."),
        ("La veille réglementaire par service",
         "Lois, décrets et circulaires paraissent sans prévenir. Chaque service découvre par ses propres moyens ce qui le concerne.",
         "Il résume les textes publiés et signale à chaque service ceux qui touchent à ses missions.",
         "Il lit le texte d'origine avant de modifier une pratique."),
    ]),
]

# Ce qu'il faut pour demarrer, exemple par exemple. Source : la note de
# faisabilite du 2026-10-01.
PREREQUIS = {
    "Le procès-verbal de séance du conseil":
        "Un enregistrement audible de la séance, et la trame de procès-verbal de la collectivité.",
    "Le projet de délibération":
        "Les modèles de délibération de la collectivité, et les éléments transmis par le service.",
    "Le projet d'arrêté":
        "Les modèles d'arrêté de la collectivité, et la demande reçue.",
    "La note de synthèse pour les élus":
        "Les rapports des services en fichiers texte, et non en images scannées.",
    "Le tri des demandes entrantes":
        "Un accès à la messagerie d'accueil, et la liste des services avec leurs attributions. Les courriers papier doivent d'abord être numérisés.",
    "La réponse de premier niveau":
        "Un accès à la messagerie d'accueil, et des informations pratiques à jour sur le site de la collectivité.",
    "Le suivi des demandes sans réponse":
        "Des demandes enregistrées dans une messagerie ou un logiciel de suivi, et un délai de réponse fixé par la collectivité.",
    "Le classement des signalements de voirie":
        "Des signalements saisis par écrit, et le découpage de la commune en secteurs.",
    "L'information municipale sur plusieurs supports":
        "Une note de départ validée, et un exemple de publication pour chaque support.",
    "Le dossier de demande de subvention":
        "Le règlement du financeur, et la description de l'opération à financer, avec son calendrier et son budget.",
    "La veille des appels à projets":
        "La liste des opérations que la collectivité cherche à financer.",
    "La trame du cahier des charges":
        "Les cahiers des charges des marchés déjà passés, et une description du besoin.",
    "La recherche dans les délibérations et les arrêtés":
        "Les délibérations et les arrêtés en fichiers texte. Les actes anciens, scannés en image, doivent d'abord être convertis.",
    "Les réponses sur les procédures internes":
        "Des procédures écrites. Celles qui ne tiennent que dans la mémoire des agents doivent d'abord être rédigées.",
    "La veille réglementaire par service":
        "La liste des missions de chaque service.",
}

cartes.greffer(
    corps="coll-agents-corps.html",
    familles=FAMILLES,
    titre="%s exemples d'agents IA pour une collectivité",
    intro="Nous les avons classés en quatre familles. Pour chacun, nous décrivons la situation de départ, ce que fait l'agent IA, ce qui reste à l'agent municipal et ce qu'il faut pour démarrer. Certains existent déjà en produit prêt à l'emploi : nous vous le disons au cadrage.",
    etiquettes=("Aujourd'hui", "L'agent IA", "L'agent municipal"),
    prerequis=PREREQUIS,
)
