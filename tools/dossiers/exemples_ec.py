# -*- coding: utf-8 -*-
"""Les dix-sept exemples d'agents de la page /expert-comptable/agents-ia/.

    python tools/dossiers/exemples_ec.py   # regenere la section dans ec-agents-corps.html
    python tools/dossiers/assembler.py agents

Regle d'ecriture : voir cartes.greffer. Faisabilite de chaque exemple :
docs/superpowers/notes/2026-10-01-faisabilite-agents.md.
"""
import cartes

# (ancre, titre de famille, [(titre, aujourd'hui, l'agent, le collaborateur[, a savoir])])
FAMILLES = [
    ("boite", "La messagerie du cabinet", [
        ("La relance des pièces manquantes",
         "Chaque mois, il faut réclamer les mêmes pièces, client par client. Les relances s'écrivent à la main et leur suivi se fait de mémoire.",
         "Il part de la liste des pièces attendues pour chaque dossier, repère celles qui manquent à l'échéance et prépare la relance au nom du collaborateur.",
         "Il relit, ajuste le ton pour un client qu'il connaît, et envoie.",
         "Certains logiciels de production relancent déjà les pièces eux-mêmes. Nous le vérifions avant de construire cet agent."),
        ("Le tri de la messagerie et les brouillons de réponse",
         "Demandes de pièces, questions ponctuelles et réclamations arrivent dans la même messagerie, pendant la production.",
         "Il classe les messages entrants par nature et par dossier, puis prépare un brouillon à partir des réponses que le cabinet a déjà validées.",
         "Il relit et envoie. Ce qui relève du conseil lui revient entièrement."),
        ("Les questions qui reviennent toute l'année",
         "Frais de repas, véhicule de société, TVA sur un cas limite. Chaque collaborateur répond de mémoire, à sa façon.",
         "Il propose une réponse à partir des fiches que le cabinet a validées, et il indique la source sur laquelle elle repose.",
         "Il vérifie que le cas du client est bien celui de la fiche, puis il envoie."),
        ("La relance des honoraires",
         "Les factures d'honoraires échues se relancent quand quelqu'un y pense, souvent tard.",
         "Il repère les factures échues dans votre outil de facturation et prépare la relance, sur un ton plus ferme à chaque rappel.",
         "Il soumet la relance à l'associé, qui choisit de l'envoyer ou d'appeler le client."),
    ]),
    ("pieces", "Les pièces et les dossiers", [
        ("Le classement des pièces reçues",
         "Les clients envoient leurs pièces en vrac : photos, PDF, pièces jointes sans nom.",
         "Il identifie chaque pièce (facture d'achat, relevé, note de frais), la renomme et la range dans le bon dossier. Il met de côté celles qu'il ne sait pas classer.",
         "Il reprend les pièces mises de côté et les classe lui-même."),
        ("La pré-saisie à partir des pièces",
         "Factures et relevés arrivent en PDF ou en photo, et sont ressaisis ligne par ligne.",
         "Il lit la pièce, en sort le tiers, la date, les montants et la taxe, puis propose une écriture pour le dossier.",
         "Il valide ou corrige chaque proposition. Rien n'est comptabilisé sans lui.",
         "Beaucoup de logiciels de production font déjà cette pré-saisie. Regardez le vôtre avant de faire construire cet agent."),
        ("Les points à regarder avant la révision",
         "Le réviseur ouvre le dossier et découvre les comptes d'attente non soldés et les écritures sans pièce.",
         "Il parcourt le fichier des écritures avant le réviseur et dresse la liste des points à regarder : comptes d'attente non soldés, écritures sans référence de pièce, écarts inhabituels d'un exercice à l'autre. Il ne dit pas si les comptes sont justes.",
         "Il révise le dossier, en commençant par les points de la liste."),
        ("La collecte des variables de paie",
         "Absences, primes et heures arrivent chaque mois dans des messages dispersés, parfois la veille de la paie.",
         "Il prépare la relance de chaque client selon le calendrier de paie, rassemble les réponses dans la trame du cabinet et signale ce qui manque.",
         "Il envoie les relances, vérifie les éléments reçus et les saisit lui-même."),
    ]),
    ("ecrits", "Les échéances et les écrits", [
        ("Le calendrier des échéances",
         "TVA, acomptes, liasses, assemblées : les dates sont suivies dans un tableur, dossier par dossier.",
         "Il tient le calendrier de chaque dossier à partir de son régime fiscal et de sa date de clôture, prévient le collaborateur à l'approche d'une échéance et prépare le message au client.",
         "Il confirme la date et envoie.",
         "Votre logiciel de production tient peut-être déjà ce calendrier."),
        ("La lettre de mission et ses avenants",
         "Le contenu de la lettre de mission est encadré par la profession. Le document, lui, se réécrit à chaque nouveau client et à chaque changement de périmètre.",
         "Il prépare le projet de lettre à partir du modèle du cabinet et de la fiche du client.",
         "Il soumet ce projet à l'associé, qui relit, ajuste et signe."),
        ("Les projets pour l'approbation des comptes",
         "Le procès-verbal d'assemblée et le rapport de gestion se réécrivent chaque année à partir de ceux de l'an passé.",
         "Il prépare les projets à partir des trames du cabinet et des éléments du dossier.",
         "Il relit chaque projet avant de l'envoyer à la signature."),
        ("Le commentaire du tableau de bord",
         "Les chiffres du mois sont prêts. Le commentaire qui les accompagne s'écrit en dernier, quand il reste du temps.",
         "Il rédige un projet de commentaire à partir des chiffres que vous avez arrêtés : ce qui a changé, et de combien.",
         "Il corrige, ajoute ce qu'il sait du client et signe. L'analyse et le conseil restent les siens."),
    ]),
    ("memoire", "Le rendez-vous et la mémoire du cabinet", [
        ("La préparation d'un rendez-vous",
         "Avant un rendez-vous, il faut rouvrir les derniers échanges, les points en suspens et les chiffres du dossier.",
         "Il réunit ces éléments dans une fiche de préparation, avec les questions restées sans réponse.",
         "Il arrive au rendez-vous avec la fiche et choisit les sujets à aborder."),
        ("Le compte rendu de rendez-vous",
         "Le compte rendu s'écrit le soir, de mémoire, après un point de situation ou une remise de bilan.",
         "À partir de vos notes, il prépare le compte rendu dans la trame du cabinet : ce qui a été dit, ce qui a été conseillé, les suites à donner.",
         "Il relit, corrige et classe. Ce compte rendu est la trace de son devoir de conseil : il en reste responsable."),
        ("La base documentaire interne",
         "Procédures, notes internes et réponses déjà données sont dispersées dans des dossiers partagés. La réponse existe, et personne ne la retrouve.",
         "Il répond en langage courant à partir des documents que le cabinet a choisi de lui confier, et il cite celui d'où vient chaque réponse.",
         "Il ouvre le document cité avant de s'en servir."),
        ("L'entrée d'un nouveau client",
         "La liste des pièces à fournir est envoyée par message. Le suivi de ce qui a été reçu se fait à la main.",
         "Il prépare la liste et les relances, suit ce qui arrive et constitue le dossier au fur et à mesure.",
         "Il envoie les demandes. Les vérifications d'identité et l'appréciation du risque restent les siennes."),
        ("La veille fiscale et sociale, appliquée à vos dossiers",
         "La veille passe après la production. Quand une mesure sort, il faut encore retrouver, un par un, les clients qu'elle concerne.",
         "Il résume les publications fiscales et sociales. À partir de la fiche de chaque dossier (forme juridique, régime fiscal, secteur), il signale ceux qu'une mesure peut concerner.",
         "Il lit le texte d'origine avant d'en parler au client.",
         "Ce rapprochement est approximatif. Il oriente la lecture, il ne remplace pas la connaissance du dossier."),
    ]),
]

# Ce qu'il faut pour demarrer, exemple par exemple. Source : la note de
# faisabilite du 2026-10-01.
PREREQUIS = {
    "La relance des pièces manquantes":
        "La liste des pièces attendues pour chaque dossier, et un accès à l'espace où les clients déposent leurs pièces.",
    "Le tri de la messagerie et les brouillons de réponse":
        "Un accès à la messagerie du cabinet, et des réponses déjà validées sur lesquelles s'appuyer.",
    "Les questions qui reviennent toute l'année":
        "Des fiches de réponse validées par le cabinet. Elles peuvent être écrites pendant la formation.",
    "La relance des honoraires":
        "Un accès à votre outil de facturation, ou à son export.",
    "Le classement des pièces reçues":
        "Un accès en écriture à l'espace où les pièces sont rangées, et votre plan de classement.",
    "La pré-saisie à partir des pièces":
        "Un accès en écriture à votre logiciel de production, et le plan de comptes de chaque dossier.",
    "Les points à regarder avant la révision":
        "Le fichier des écritures comptables du dossier, que tout logiciel exporte, et celui de l'exercice précédent.",
    "La collecte des variables de paie":
        "Un accès à la messagerie, le calendrier de paie et la trame de collecte du cabinet.",
    "Le calendrier des échéances":
        "Pour chaque dossier, la forme juridique, le régime fiscal et la date de clôture.",
    "La lettre de mission et ses avenants":
        "Le modèle de lettre de mission du cabinet, et la fiche du client.",
    "Les projets pour l'approbation des comptes":
        "Les trames du cabinet, et les comptes annuels arrêtés.",
    "Le commentaire du tableau de bord":
        "Les chiffres arrêtés du mois et ceux de la période de comparaison, dans un tableau que l'agent peut lire.",
    "La préparation d'un rendez-vous":
        "Un accès aux échanges avec le client et aux chiffres de son dossier.",
    "Le compte rendu de rendez-vous":
        "Vos notes de rendez-vous, et la trame de compte rendu du cabinet.",
    "La base documentaire interne":
        "Des procédures écrites et à jour. L'agent ne répond qu'à partir de ce que le cabinet lui a confié.",
    "L'entrée d'un nouveau client":
        "La liste des pièces que le cabinet exige, et un accès à la messagerie ou au portail de dépôt.",
    "La veille fiscale et sociale, appliquée à vos dossiers":
        "Une fiche par dossier : forme juridique, régime fiscal, secteur.",
}

cartes.greffer(
    corps="ec-agents-corps.html",
    familles=FAMILLES,
    titre="%s exemples d'agents IA pour un cabinet comptable",
    intro="Nous les avons classés selon l'endroit du cabinet où ils interviennent. Pour chacun, nous décrivons la situation de départ, ce que fait l'agent IA, ce qui reste au collaborateur et ce qu'il faut pour démarrer. Certains existent déjà dans des logiciels de production : nous le vérifions avant de construire un agent.",
    etiquettes=("Aujourd'hui", "L'agent IA", "Le collaborateur"),
    prerequis=PREREQUIS,
)
