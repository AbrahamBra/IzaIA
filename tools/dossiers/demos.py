# -*- coding: utf-8 -*-
"""Les demonstrations animees des cartes d'exemples.

Une demonstration, c'est un dessin (demos/<nom>.svg), une voix off et son
minutage (demos/<nom>.json). La voix dit une phrase par scene ; le minutage
donne l'instant ou chaque phrase commence, et c'est lui qui fait avancer le
dessin. Le lecteur est styles/demo-agent.js.

La narration suit toujours la meme trame, en quatre temps :
    1. Aujourd'hui, ...                la situation de depart
    2. Demain, a l'aide d'un agent IA  ce que l'agent IA produit
    3. le benefice                     ce que cela change pour l'agent municipal
    4. IZAIA est la pour ...           ce que nous faisons

    python tools/dossiers/demos.py voix pv-seance   # (re)genere la voix et le minutage
    python tools/dossiers/exemples_coll.py          # regreffe les cartes
    python tools/dossiers/assembler.py coll-agents

La cle ElevenLabs se lit dans le fichier .env du dossier parent du site, hors
du depot : ELEVENLABS_API_KEY=...
"""
import base64
import html
import io
import json
import os
import re
import subprocess
import sys
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(ICI))
DOSSIER = os.path.join(ICI, "demos")

# Deux voix de la bibliotheque francaise d'ElevenLabs (l'API ne les sert qu'aux
# comptes abonnes), avec le modele v4, plus naturel que Multilingual v2, retenu a
# l'ecoute le 3 octobre 2026. Les demonstrations alternent les deux voix.
NICOLAS = "aQROLel5sQbj1vuIVi6B"   # « Nicolas - Narrator »
CLAIRE = "6vTyAgAT8PncODBcLjRf"    # « Claire - Warm, Pretty and Charming »
MODELE = "eleven_v4"

# Ce que la voix doit lire autrement que ce qui s'ecrit (meme regle que la VSL).
PRONONCIATION = [(r"\bIZAIA\b", "Izaïa")]

# Dans un dessin, l'endroit ou vient la scene IZAIA (demos/_izaia.svg).
MARQUE = "<!-- IZAIA -->"

# Apres la voix, le logo s'anime seul pendant quelques secondes.
LOGO = 4.5

# Une animation part un peu avant le mot qui la declenche.
AVANCE = 0.15

# La derniere scene est la meme dans toutes les demonstrations : c'est la signature.
FIN = ("IZAIA est là pour vous aider à choisir. Nous regardons d'abord si un produit fait déjà ce travail. "
       "Nous ne construisons un agent IA que s'il le faut. Et nous vous disons quand il n'est pas à construire : "
       "quand il est question de relation humaine, d'arbitrage, de décision. "
       "Là, l'intelligence dont vous avez besoin n'a rien d'artificiel.")
MOTS_FIN = ["vous aider à choisir", "regardons d'abord", "ne construisons", "nous vous disons", "Là, l'intelligence"]

# nom : (dossier de la page, voix, etapes).
# Une etape = (repere affiche, phrase dite, mots qui declenchent une animation).
# Le dessin retrouve l'instant du n-ieme mot de la scene s dans --c<s>-<n>.
DEMOS = {
    "pv-seance": (os.path.join("collectivites", "agents-ia"), NICOLAS, [
        ("Aujourd'hui",
         "Aujourd'hui, après chaque conseil, quelqu'un dans votre mairie réécoute la séance pour écrire le procès-verbal.",
         []),
        ("Demain",
         "Demain, vous confiez l'enregistrement à un agent IA. Il prépare le projet de procès-verbal, dans votre trame : l'ordre du jour, les interventions, les votes.",
         ["Il prépare", "votre trame", "l'ordre du jour", "les interventions", "les votes"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il n'a plus à tout réécouter ni à tout retaper. Il part d'un texte déjà écrit et vérifie que la transcription est bonne : l'exactitude d'un vote, l'orthographe d'un nom de famille, les chiffres clés. C'est du temps libéré sur une tâche chronophage, et réinvesti au service de vos administrés.",
         ["tout réécouter", "tout retaper", "vérifie", "d'un vote", "d'un nom", "les chiffres", "du temps libéré"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
    "tri-demandes": (os.path.join("collectivites", "agents-ia"), NICOLAS, [
        ("Aujourd'hui",
         "Aujourd'hui, les courriels et les formulaires du site arrivent dans la même messagerie. Quelqu'un dans votre mairie les ouvre un par un pour les transmettre au bon service.",
         ["les ouvre un par un"]),
        ("Demain",
         "Demain, un agent IA lit chaque demande écrite et vous propose le service à qui la transmettre : un permis de construire part à l'urbanisme, un nid-de-poule à la voirie, une inscription à la cantine aux écoles.",
         ["lit chaque demande", "un permis de construire", "un nid-de-poule", "une inscription"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il n'a plus à trier chaque message à la main. Il valide le service proposé, ou en choisit un autre. C'est du temps libéré sur une tâche répétitive, et réinvesti au service de vos administrés.",
         ["trier chaque message", "Il valide", "en choisit un autre", "du temps libéré"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
    "courriers-maire": (os.path.join("collectivites", "agents-ia"), CLAIRE, [
        ("Aujourd'hui",
         "Aujourd'hui, les habitants, les associations et les entreprises écrivent au maire. Pour chaque lettre, quelqu'un dans votre mairie retrouve ce que la commune a déjà décidé sur le sujet, rédige la réponse, puis la glisse dans le parapheur pour que le maire la signe.",
         ["écrivent au maire", "le parapheur"]),
        ("Demain",
         "Demain, un agent IA lit la lettre reçue et écrit une première réponse. Il s'appuie sur ce que le conseil municipal a déjà voté sur le sujet, et sur les réponses que la mairie a déjà faites à des demandes semblables. Par exemple, le club de basket demande un créneau de plus au gymnase. La réponse rappelle le planning des salles voté par le conseil, et la convention signée avec le club.",
         ["écrit une première réponse", "le club de basket", "le planning des salles", "la convention signée"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il ne part plus d'une page blanche, et il n'a plus à chercher ce que la commune a déjà répondu. Il relit la réponse, l'ajuste si besoin, puis la met au parapheur. Le maire signe une lettre cohérente avec les décisions de la commune.",
         ["page blanche", "Il relit", "la met au parapheur", "Le maire signe"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
    "fiche-rdv": (os.path.join("collectivites", "agents-ia"), NICOLAS, [
        ("Aujourd'hui",
         "Aujourd'hui, avant de recevoir une association ou une entreprise, le maire veut savoir où en est la commune avec elle. Pour le lui dire, quelqu'un doit fouiller plusieurs dossiers : les subventions, les conventions, le courrier.",
         ["où en est la commune", "fouiller plusieurs dossiers"]),
        ("Demain",
         "Demain, la veille du rendez-vous, un agent IA rassemble sur une seule page ce que la commune a voté, signé ou écrit pour cet interlocuteur. Pour le comité des fêtes, par exemple, la fiche indique la subvention votée l'an dernier, la convention de prêt de matériel et le dernier courrier reçu. L'agent IA ne prépare jamais de fiche sur un habitant, seulement sur un organisme.",
         ["rassemble sur une seule page", "la subvention votée", "la convention de prêt", "le dernier courrier", "jamais de fiche"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il ne fouille plus les dossiers la veille du rendez-vous. Il vérifie chaque ligne de la fiche dans le document d'où elle vient, puis la remet à l'élu. L'élu reçoit son interlocuteur en connaissant déjà l'historique.",
         ["ne fouille plus", "Il vérifie chaque ligne", "la remet à l'élu", "L'élu reçoit"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
    "budget-clair": (os.path.join("collectivites", "agents-ia"), CLAIRE, [
        ("Aujourd'hui",
         "Aujourd'hui, la loi vous demande de publier chaque année, avec le budget, une présentation courte et claire pour les habitants. Quelqu'un dans votre mairie l'écrit à partir de documents comptables de plusieurs centaines de pages.",
         ["la loi vous demande", "documents comptables"]),
        ("Demain",
         "Demain, un agent IA lit le budget voté par le conseil et en écrit une première version en mots simples. Il explique combien coûte le fonctionnement de la commune, ce qu'elle investit cette année, comme la rénovation de la médiathèque, et comment évolue sa dette.",
         ["lit le budget voté", "le fonctionnement", "la rénovation de la médiathèque", "sa dette"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il n'a plus à traduire chaque année des tableaux comptables en phrases. Il vérifie chaque chiffre dans le budget, puis soumet la présentation aux élus, qui la relisent avant sa publication sur le site. Chaque habitant peut lire à quoi sert l'argent de sa commune.",
         ["n'a plus à traduire", "Il vérifie chaque chiffre", "soumet la présentation aux élus", "Chaque habitant"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
    "deliberation": (os.path.join("collectivites", "agents-ia"), CLAIRE, [
        ("Aujourd'hui",
         "Aujourd'hui, pour chaque délibération, quelqu'un dans votre mairie repart d'une ancienne et la reprend à la main, des visas jusqu'au dispositif.",
         ["repart d'une ancienne", "des visas"]),
        ("Demain",
         "Demain, le service transmet ses éléments à un agent IA : l'objet, les montants, les dates. Il prépare le projet de délibération dans vos modèles.",
         ["l'objet", "les montants", "les dates", "Il prépare"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il ne recopie plus une ancienne délibération en changeant les dates une à une. Il vérifie les visas et la compétence du conseil, puis transmet le projet à l'élu qui le rapporte. Il passe son temps là où il compte : sur la solidité juridique de l'acte.",
         ["ne recopie plus", "vérifie les visas", "la compétence", "transmet le projet", "là où il compte"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
    "arrete": (os.path.join("collectivites", "agents-ia"), NICOLAS, [
        ("Aujourd'hui",
         "Aujourd'hui, les mêmes arrêtés reviennent sans cesse : la circulation, l'occupation du domaine public, les travaux de voirie. Et à chaque fois, aucune mention obligatoire ne doit manquer.",
         ["la circulation", "l'occupation", "les travaux de voirie", "aucune mention"]),
        ("Demain",
         "Demain, un agent IA part de la demande reçue et de votre modèle d'arrêté. Il prépare le projet, avec les mentions prévues par votre modèle.",
         ["la demande reçue", "votre modèle d'arrêté", "Il prépare", "les mentions"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il ne repart plus d'un ancien arrêté à adapter. Il vérifie les dates, les lieux et le fondement juridique, puis présente le projet à la signature. Il garde son attention pour ce qui engage la commune : le bon fondement, le bon endroit, les bonnes dates.",
         ["ne repart plus", "vérifie les dates", "les lieux", "le fondement juridique", "à la signature", "Il garde son attention"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
    "note-elus": (os.path.join("collectivites", "agents-ia"), CLAIRE, [
        ("Aujourd'hui",
         "Aujourd'hui, avant chaque conseil, quelqu'un dans votre mairie résume les rapports des services pour les élus. Souvent au dernier moment.",
         ["résume les rapports", "au dernier moment"]),
        ("Demain",
         "Demain, un agent IA lit chaque rapport et prépare une note courte : l'objet, les montants en jeu, la décision demandée.",
         ["lit chaque rapport", "une note courte", "l'objet", "les montants", "la décision"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il ne résume plus chaque rapport dans l'urgence. Il relit chaque note en ouvrant le rapport d'origine : c'est lui qui garantit ce que lisent les élus. Et vos élus arrivent au conseil en sachant sur quoi ils votent.",
         ["ne résume plus", "Il relit", "le rapport d'origine", "c'est lui qui garantit", "vos élus"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
    "reponse-accueil": (os.path.join("collectivites", "agents-ia"), NICOLAS, [
        ("Aujourd'hui",
         "Aujourd'hui, les mêmes questions reviennent chaque semaine par courriel : les horaires de la mairie, les pièces à fournir pour une démarche, la façon de la faire en ligne. Et quelqu'un dans votre mairie répond chaque fois la même chose, à la main.",
         ["les horaires", "les pièces à fournir", "en ligne", "répond chaque fois"]),
        ("Demain",
         "Demain, un agent IA lit la question et prépare une réponse. Il s'appuie seulement sur les informations que la mairie a déjà publiées sur son site. Par exemple, un habitant veut louer la salle des fêtes pour un anniversaire. La réponse donne les tarifs votés par le conseil, le montant de la caution, et rappelle qu'il faut une attestation d'assurance.",
         ["prépare une réponse", "publiées sur son site", "la salle des fêtes", "les tarifs votés", "la caution", "attestation d'assurance"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il n'a plus à retaper chaque semaine la même explication. Il relit la réponse, la complète si la demande sort de l'ordinaire, puis l'envoie lui-même. Aucune réponse ne part sans lui. Et la personne qui écrit à la mairie a tout ce qu'il lui faut dès la première réponse.",
         ["retaper", "Il relit", "l'envoie lui-même", "Aucune réponse", "dès la première réponse"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
    "signalements": (os.path.join("collectivites", "agents-ia"), CLAIRE, [
        ("Aujourd'hui",
         "Aujourd'hui, les signalements arrivent de partout : par téléphone, par courriel, par le formulaire du site. Chaque habitant décrit le problème à sa façon, et souvent plusieurs habitants signalent le même. Quelqu'un dans votre mairie remet tout cela au propre, une fiche après l'autre, pour les services techniques.",
         ["par téléphone", "par courriel", "le formulaire du site", "à sa façon", "remet tout cela au propre"]),
        ("Demain",
         "Demain, quand un habitant appelle, la personne à l'accueil remplit pendant l'appel le formulaire de signalement du site, comme il l'aurait fait lui-même. Tout arrive alors par écrit. Un agent IA lit chaque signalement et le classe par nature : un trottoir abîmé, un panneau tombé, un dépôt sauvage. Il les range aussi par quartier. Et quand trois habitants signalent le même dépôt, il regroupe leurs trois messages sur une seule fiche.",
         ["remplit pendant l'appel", "par écrit", "un trottoir abîmé", "un panneau tombé", "un dépôt sauvage", "par quartier", "une seule fiche"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il n'a plus à remettre chaque message au propre pour en faire une fiche. Il vérifie chaque fiche et décide de la priorité. Vos équipes partent sur le terrain en sachant où aller et ce qu'elles vont trouver.",
         ["remettre chaque message", "Il vérifie chaque fiche", "la priorité", "Vos équipes"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
    "info-supports": (os.path.join("collectivites", "agents-ia"), NICOLAS, [
        ("Aujourd'hui",
         "Aujourd'hui, une même information doit paraître sur le site de la commune, sur ses réseaux sociaux, sur l'application municipale et sur les panneaux d'affichage. Chaque support a sa longueur et son ton. Alors quelqu'un dans votre mairie réécrit la même information plusieurs fois.",
         ["le site de la commune", "ses réseaux sociaux", "l'application municipale", "les panneaux d'affichage", "réécrit"]),
        ("Demain",
         "Demain, vous donnez une seule note à un agent IA : la collecte des encombrants aura lieu le 8 avril. Il en écrit une version pour chaque support : un article pour le site, un message court pour les réseaux sociaux et l'application, une affiche pour les panneaux.",
         ["une seule note", "le 8 avril", "un article", "un message court", "une affiche"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il n'a plus à reformuler la même annonce pour chaque support. Il vérifie la date, les rues concernées et ce que les habitants ont le droit de sortir, puis publie. Et l'habitant lit la même date, qu'il regarde l'affiche ou son téléphone.",
         ["reformuler", "Il vérifie la date", "les rues concernées", "le droit de sortir", "puis publie", "qu'il regarde l'affiche"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
    "subvention-detr": (os.path.join("collectivites", "agents-ia"), CLAIRE, [
        ("Aujourd'hui",
         "Aujourd'hui, chaque financeur a son règlement, son formulaire et sa liste de pièces à joindre. Pour monter un dossier, quelqu'un dans votre mairie relit le règlement ligne à ligne, pour ne rien oublier.",
         ["chaque financeur", "ligne à ligne"]),
        ("Demain",
         "Demain, un agent IA lit le règlement de l'aide que vous visez. Par exemple, l'appel à projets de la préfecture pour la dotation d'équipement des territoires ruraux, afin de rendre la mairie accessible aux personnes handicapées. Il relève les conditions à remplir, les pièces à joindre et la date limite. Puis il prépare une première version du dossier, avec la description des travaux.",
         ["l'appel à projets", "rendre la mairie accessible", "les conditions à remplir", "les pièces à joindre", "la date limite", "une première version"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il n'a plus à relire le règlement pour dresser la liste des pièces. Il vérifie chaque condition dans le texte de la préfecture. Puis il passe son temps sur le plan de financement, que le conseil municipal adopte par délibération. Le dossier part complet, avant la date limite.",
         ["dresser la liste", "Il vérifie chaque condition", "le plan de financement", "adopte par délibération", "Le dossier part complet"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
    "cahier-charges": (os.path.join("collectivites", "agents-ia"), NICOLAS, [
        ("Aujourd'hui",
         "Aujourd'hui, quand un marché arrive à son terme, quelqu'un dans votre mairie reprend le cahier des charges de l'ancien marché. Il le relit en entier pour voir ce qui doit changer.",
         ["reprend le cahier des charges", "le relit en entier"]),
        ("Demain",
         "Demain, vous expliquez votre besoin à un agent IA. Par exemple, l'entretien des espaces verts de la commune pendant trois ans, avec la tonte et la taille des haies. Il prépare une première trame du cahier des charges. Il y reprend les clauses de vos anciens marchés qui sont encore valables. Il ne lit pas les offres des entreprises, et il ne les note pas.",
         ["vous expliquez votre besoin", "des espaces verts", "la tonte", "la taille des haies", "une première trame", "encore valables", "il ne les note pas"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il n'a plus à relire tout l'ancien marché. À la place, il définit le besoin et les critères pour choisir l'entreprise, puis il complète la trame. Le nouveau cahier des charges décrit le besoin actuel de la commune. Et c'est toujours la commune qui choisit l'entreprise.",
         ["relire tout l'ancien marché", "il définit le besoin", "les critères", "il complète la trame", "le besoin actuel", "c'est toujours la commune"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
    "recherche-actes": (os.path.join("collectivites", "agents-ia"), CLAIRE, [
        ("Aujourd'hui",
         "Aujourd'hui, pour retrouver ce que le conseil a voté sur un sujet il y a six ans, il faut savoir dans quel registre chercher. Ou trouver la personne qui s'en souvient.",
         ["dans quel registre", "qui s'en souvient"]),
        ("Demain",
         "Demain, vous posez votre question à un agent IA, en français courant. Par exemple : combien coûte une place au marché du samedi ? Il cherche dans vos délibérations et vos arrêtés numérisés, puis il répond en quelques mots. Il indique aussi la délibération qui a fixé ce tarif, avec sa date et son numéro.",
         ["vous posez votre question", "combien coûte une place", "Il cherche", "il répond en quelques mots", "Il indique aussi", "sa date et son numéro"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il n'a plus à feuilleter des années de registres. Il ouvre la délibération indiquée et la lit avant de répondre. Quand un élu ou un commerçant du marché pose la question, il a la réponse et le texte qui la justifie.",
         ["feuilleter", "Il ouvre la délibération", "un commerçant", "le texte qui la justifie"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
    "procedures": (os.path.join("collectivites", "agents-ia"), NICOLAS, [
        ("Aujourd'hui",
         "Aujourd'hui, les procédures de votre mairie sont dans des notes rangées un peu partout, ou dans la tête des plus anciens. Quand l'un d'eux part à la retraite, une partie de ce savoir part avec lui.",
         ["rangées un peu partout", "dans la tête", "part à la retraite"]),
        ("Demain",
         "Demain, une nouvelle recrue demande à un agent IA comment faire un bon de commande. Il répond à partir des procédures écrites de la mairie, et il donne le nom de la note où il a trouvé la réponse. Si la procédure n'est écrite nulle part, il répond qu'il n'a trouvé aucune note sur ce sujet.",
         ["une nouvelle recrue", "un bon de commande", "procédures écrites", "le nom de la note", "aucune note"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il ne fait plus le tour des bureaux pour trouver le collègue qui connaît la procédure. Il ouvre la note indiquée pour vérifier, et il prévient son responsable si une procédure n'est plus à jour. Et une procédure écrite sert à tous, même après le départ de celui qui l'a rédigée.",
         ["le tour des bureaux", "Il ouvre la note", "il prévient son responsable", "sert à tous"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
    "veille": (os.path.join("collectivites", "agents-ia"), CLAIRE, [
        ("Aujourd'hui",
         "Aujourd'hui, de nouveaux décrets changent régulièrement le travail des mairies. Les repérer prend du temps. Alors on découvre parfois un changement tard, par un collègue d'une autre commune.",
         ["de nouveaux décrets", "prend du temps", "un collègue d'une autre commune"]),
        ("Demain",
         "Demain, un agent IA lit chaque matin les textes parus au Journal officiel. Parmi ces textes, il repère ceux qui changent une règle que votre mairie applique. Pour chacun, il écrit en quelques lignes ce qui change, et il l'envoie au service qui applique cette règle. Par exemple, un nouveau décret modifie les règles de l'accueil périscolaire. Le service enfance reçoit un résumé des nouvelles règles.",
         ["au Journal officiel", "il repère", "en quelques lignes", "il l'envoie", "l'accueil périscolaire", "Le service enfance"]),
        ("Le bénéfice",
         "Ce que votre agent municipal y gagne : il n'a plus à éplucher le Journal officiel et les lettres d'information. Il lit le décret lui-même avant de changer quoi que ce soit dans sa façon de faire. Et votre mairie applique une nouvelle règle dès qu'elle entre en vigueur.",
         ["éplucher", "Il lit le décret", "changer quoi que ce soit", "dès qu'elle entre en vigueur"]),
        ("IZAIA",
         FIN,
         MOTS_FIN),
    ]),
}


def dit(phrase):
    for motif, lecture in PRONONCIATION:
        phrase = re.sub(motif, lecture, phrase)
    return phrase


def bloc(nom):
    """Le HTML de la demonstration, a glisser dans la carte."""
    _, _, etapes = DEMOS[nom]
    with io.open(os.path.join(DOSSIER, nom + ".svg"), encoding="utf-8") as fh:
        dessin = fh.read().strip()
    # La derniere scene est la meme partout : c'est la signature.
    with io.open(os.path.join(DOSSIER, "_izaia.svg"), encoding="utf-8") as fh:
        assert dessin.count(MARQUE) == 1, "repere de la scene IZAIA absent de %s.svg" % nom
        dessin = dessin.replace(MARQUE, fh.read().strip())
    with io.open(os.path.join(DOSSIER, nom + ".json"), encoding="utf-8") as fh:
        minutage = json.load(fh)
    assert minutage["phrases"] == [e[1] for e in etapes] and minutage["mots"] == [e[2] for e in etapes], (
        "la voix de %s ne dit plus le texte : relancer demos.py voix %s" % (nom, nom))
    cles = ";".join("--c%d-%d:%.3f" % (s + 1, n + 1, q)
                    for s, scene in enumerate(minutage["cles"]) for n, q in enumerate(scene))
    e = html.escape
    l = []
    # La derniere scene, le logo, commence quand la voix s'arrete.
    total = minutage["duree"] + LOGO
    l.append('<div class="demo" data-scene="0" data-src="demos/%s.mp3" data-debuts="%s" data-voix="%.2f" data-duree="%.2f" style="%s">'
             % (nom, " ".join("%.2f" % d for d in minutage["debuts"] + [minutage["duree"]]),
                minutage["duree"], total, cles))
    l.append('  <div class="demo-scene">')
    l.append("    " + dessin.replace("\n", "\n    "))
    l.append('    <button type="button" class="demo-lire" aria-label="Lire la vidéo, %d secondes, avec le son">' % round(total))
    l.append('      <span class="demo-ico" aria-hidden="true"></span>')
    l.append('      <span class="demo-dur">%d s, avec le son</span>' % round(total))
    l.append('    </button>')
    l.append('    <span class="demo-avance" aria-hidden="true"></span>')
    l.append('    <div class="demo-barre">')
    l.append('      <button type="button" class="demo-pp" aria-label="Lire" title="Lire">'
             '<svg viewBox="0 0 16 16" aria-hidden="true"><path class="i-lire" d="M4.5 2.5v11l9-5.5z"/>'
             '<path class="i-pause" d="M4 2.5h3v11H4zM9 2.5h3v11H9z"/></svg></button>')
    l.append('      <button type="button" class="demo-debut" aria-label="Revenir au début" title="Revenir au début">'
             '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 2.5h2v11H3zM13.5 2.5v11L6 8z"/></svg></button>')
    l.append('      <input class="demo-temps" type="range" min="0" max="1000" value="0" aria-label="Position dans la vidéo">')
    l.append('      <span class="demo-chrono">0:00 / %s</span>' % "%d:%02d" % divmod(round(total), 60))
    l.append('    </div>')
    l.append('  </div>')
    l.append('  <ol class="demo-etapes">')
    for etape in etapes:
        l.append("    <li>%s</li>" % e(etape[0], quote=False))
    l.append('  </ol>')
    # Le sous-titre est construit par le lecteur a partir de la transcription,
    # pour que chaque phrase n'apparaisse qu'une fois dans la page.
    l.append('  <p class="demo-st" aria-hidden="true"></p>')
    l.append('  <details class="demo-trans">')
    l.append('    <summary>Lire la transcription</summary>')
    for etape in etapes:
        if etape[1] != FIN:
            l.append("    <p>%s</p>" % e(etape[1], quote=False))
    l.append('  </details>')
    l.append('</div>')
    return "\n".join(l)


def cle():
    chemin = os.path.join(os.path.dirname(SITE), ".env")
    with io.open(chemin, encoding="utf-8-sig") as fh:
        for ligne in fh:
            if ligne.strip().startswith("ELEVENLABS_API_KEY="):
                return ligne.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("ELEVENLABS_API_KEY absente de " + chemin)


def appel(chemin, corps=None):
    req = urllib.request.Request(
        "https://api.elevenlabs.io" + chemin,
        data=json.dumps(corps).encode("utf-8") if corps is not None else None,
        headers={"xi-api-key": cle(), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def voix(nom):
    page, ident, etapes = DEMOS[nom]
    lues = [dit(e[1]) for e in etapes]
    # Controle avant l'appel : une voix generee pour rien est facturee quand meme.
    for etape, lue in zip(etapes, lues):
        for mot in etape[2]:
            assert lue.count(mot) == 1, "mot declencheur absent ou ambigu : %s" % mot
    texte = " ".join(lues)
    rep = appel("/v1/text-to-speech/%s/with-timestamps?output_format=mp3_44100_128" % ident, {
        "text": texte, "model_id": MODELE,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    })
    al = rep["alignment"]
    assert "".join(al["characters"]) == texte, "l'alignement ne suit pas le texte"
    instants = al["character_start_times_seconds"]
    duree = round(al["character_end_times_seconds"][-1], 2)
    debuts, positions, position = [], [], 0
    for lue in lues:
        debuts.append(round(instants[position], 2))
        positions.append(position)
        position += len(lue) + 1
    # Chaque mot declencheur devient une fraction de la duree de sa scene.
    cles = []
    for s, (etape, lue) in enumerate(zip(etapes, lues)):
        fin = debuts[s + 1] if s + 1 < len(debuts) else duree
        scene = []
        for mot in etape[2]:
            assert lue.count(mot) == 1, "mot declencheur absent ou ambigu : %s" % mot
            instant = instants[positions[s] + lue.index(mot)] - AVANCE
            scene.append(round(max(0.0, (instant - debuts[s]) / (fin - debuts[s])), 3))
        cles.append(scene)
    cible = os.path.join(SITE, page, "demos")
    os.makedirs(cible, exist_ok=True)
    brut = os.path.join(DOSSIER, nom + ".brut.mp3")
    with open(brut, "wb") as fh:
        fh.write(base64.b64decode(rep["audio_base64"]))
    # Une voix seule n'a pas besoin de stereo : mono a 64 kbit/s, moitie moins lourd.
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", brut, "-ac", "1", "-b:a", "64k",
                           os.path.join(cible, nom + ".mp3")])
    os.remove(brut)
    with io.open(os.path.join(DOSSIER, nom + ".json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"phrases": [e[1] for e in etapes], "mots": [e[2] for e in etapes],
                   "debuts": debuts, "cles": cles, "duree": duree}, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(nom, ":", len(texte), "caracteres,", duree, "s, debuts", debuts, "cles", cles)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "voix" and sys.argv[2] in DEMOS:
        voix(sys.argv[2])
    else:
        raise SystemExit(__doc__)
