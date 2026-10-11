# ==============================================================================
# GÉNÉRATEUR DE FICHES INDIVIDUELLES DE CORRECTION (1 PAGE PAR ÉLÈVE)
# BTS CIEL 1 — MICROPYTHON RP2040 (15 ÉLÈVES)
# ==============================================================================
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

FICHES = [
    {
        "rang": 1,
        "nom": "DEVIER",
        "note": 18.50,
        "mention": "Très Bien (Major de promotion)",
        "scores": {
            "A1": (2.75, 3.0, "Remarquable explication de la boucle anti-répétition (a calculé que sans elle le compteur monterait à 2000 en 2s). Mentionne l'instabilité de l'entrée flottante."),
            "A2": (3.75, 4.0, "Parfaite analyse de la fonction jouer_note, des 3 itérations (300, 500, 700) et de la réduction de volume de moitié à 1000 Hz."),
            "B1": (2.00, 2.0, "Sans faute. Définition rigoureuse de la grandeur binaire (0/1) vs continue (0 à 3.3V). Valeurs de quantification exactes (0, 32767.5, 65535)."),
            "B2": (1.00, 2.0, "Formule f = 1/T et calcul de 500 Hz parfaits avec conversion d'unités (0.002s). Rapport cyclique non abordé."),
            "C1": (3.00, 3.0, "Sans faute absolu. Boucle for i in range(nb_bips), temporisations précises, inversion des états et extinction finale respectée."),
            "C2": (6.00, 6.0, "Le seul de la classe à avoir codé 100% du cahier des charges : test actif bas du PULL_UP (== 0) pour le BP et rapport proportionnel en plage 3 !")
        },
        "points_forts": "Rigueur algorithmique exceptionnelle, compréhension fine du matériel temps réel et propreté de code remarquable.",
        "axes_progres": "Penser à traiter la question sur le rapport cyclique (Ex B.2 Q2) pour atteindre le 20/20.",
        "conseil": "Excellent niveau pour un début de première année. Continuez sur cette lancée !"
    },
    {
        "rang": 2,
        "nom": "RICHARD",
        "note": 18.00,
        "mention": "Très Bien",
        "scores": {
            "A1": (2.50, 3.0, "Très bonne intuition physique : compare l'entrée flottante à une antenne/touche tactile. Rôle anti-répétition parfaitement expliqué."),
            "A2": (4.00, 4.0, "Sans faute absolu sur l'analyse modulaire PWM : 3 itérations (300, 500, 700), coupure sonore et rapport cyclique de 25% impeccables."),
            "B1": (1.00, 2.0, "Connaît la plage 0 à 65535 et l'utilité des seuils numériques. Attention à ne pas inverser les définitions GPIO et ADC."),
            "B2": (1.75, 2.0, "Calcul de fréquence 500 Hz rigoureux avec conversion d'unités. Définition et calcul du rapport cyclique (25%) bien menés."),
            "C1": (3.00, 3.0, "Code parfait : boucle for, alternance allumage/extinction cadencée et extinction finale."),
            "C2": (5.75, 6.0, "Très beau programme : toutes les plages de tension, les LEDs, le bouton et le buzzer proportionnel sont implémentés avec cadencement.")
        },
        "points_forts": "Excellente logique de programmation, syntaxe Python maîtrisée et très bonne compréhension des systèmes embarqués.",
        "axes_progres": "Veiller à bien formaliser la définition du signal analogique quantifié par le CAN.",
        "conseil": "Prestation de très haute qualité. Félicitations !"
    },
    {
        "rang": 3,
        "nom": "TREIBER",
        "note": 17.75,
        "mention": "Très Bien",
        "scores": {
            "A1": (2.75, 3.0, "L'un des seuls à mentionner explicitement la sensibilité aux parasites d'une broche flottante. Explication parfaite du compteur sans pause."),
            "A2": (3.25, 4.0, "3 itérations trouvées, fréquence 1000 Hz et calcul du rapport cyclique 25% parfaits. Attention à donner les valeurs 300, 500, 700 et non juste le pas."),
            "B1": (1.75, 2.0, "Très bonne distinction TOR vs continu. Les 3 valeurs de quantification (0, 32768, 65535) sont exactes."),
            "B2": (2.00, 2.0, "Sans faute : formule, calcul de 500 Hz avec conversion d'unités et rapport cyclique de 25% impeccablement calculés."),
            "C1": (3.00, 3.0, "Sans faute absolu sur la fonction clignotement_alerte : algorithme propre, indenté et fonctionnel."),
            "C2": (5.00, 6.0, "Configuration matérielle et structure de boucle complètes avec gestion des 3 seuils de tension et cadencement.")
        },
        "points_forts": "Grande rigueur scientifique sur les calculs physiques et excellente maîtrise de la programmation MicroPython.",
        "axes_progres": "Bien expliciter les listes de valeurs successives dans les boucles for.",
        "conseil": "Très beau travail, travaillez avec cette même régularité."
    },
    {
        "rang": 4,
        "nom": "CRIT",
        "note": 16.25,
        "mention": "Très Bien",
        "scores": {
            "A1": (2.25, 3.0, "Logique inversée du pull-up bien comprise (1 = repos, 0 = appui). Rôle anti-répétition du compteur bien analysé."),
            "A2": (3.75, 4.0, "3 itérations exactes (300, 500, 700), rôle de duty_u16(0) pour couper le son bien expliqué, fréquence et demi-volume justifiés."),
            "B1": (1.75, 2.0, "Très bonne définition du signal numérique binaire vs analogique continu. Valeurs 0 et 65535 bien indiquées."),
            "B2": (1.00, 2.0, "Fréquence 500 Hz calculée avec rigueur sur la conversion de période (0.002s)."),
            "C1": (2.50, 3.0, "Boucle for et alternance temporelle bien écrites avec les bons arguments."),
            "C2": (5.00, 6.0, "Mini-projet bien structuré avec gestion propre des 3 plages et cadencement temporel de fin de boucle.")
        },
        "points_forts": "Démarche méthodique, code propre et compréhension claire des entrées/sorties numériques et analogiques.",
        "axes_progres": "Penser à traiter le calcul du rapport cyclique en Partie B.",
        "conseil": "Très bon devoir, continuez ainsi !"
    },
    {
        "rang": 5,
        "nom": "GUILLOT",
        "note": 14.25,
        "mention": "Bien",
        "scores": {
            "A1": (2.00, 3.0, "Bonne identification du niveau logique de repos à 1 et de l'appui à 0. Évitement de l'état instable mentionné."),
            "A2": (3.75, 4.0, "3 itérations avec valeurs 300, 500, 700 exactes. Rôle de coupure sonore et fréquence 1000 Hz bien trouvés."),
            "B1": (2.00, 2.0, "Remarquable réponse : définit parfaitement le TOR binaire (1=3.3V, 0=0V) face à la tension continue. Tableau 0, 32768, 65535 sans faute."),
            "B2": (1.00, 2.0, "Formule et calcul de 500 Hz bien maîtrisés avec prise en compte des millisecondes."),
            "C1": (1.50, 3.0, "La séquence temporelle allumage/pause/extinction est comprise, mais attention à la syntaxe (utiliser for i in range et non while)."),
            "C2": (4.00, 6.0, "Bonne configuration des broches et pose correcte des plages de détection analogique.")
        },
        "points_forts": "Très bonnes bases théoriques sur l'électronique numérique et l'échantillonnage ADC.",
        "axes_progres": "Revoir la syntaxe standard des boucles for en Python pour le parcours d'un nombre de répétitions.",
        "conseil": "Devoir solide et sérieux, de réelles capacités."
    },
    {
        "rang": 6,
        "nom": "BOUSSAGUET",
        "note": 13.50,
        "mention": "Assez Bien",
        "scores": {
            "A1": (1.75, 3.0, "Comprend la fixation au repos à 1 et l'instabilité de l'état flottant. Définition du rôle anti-rebond un peu courte."),
            "A2": (3.25, 4.0, "Boucle for à 3 passages (300, 500, 700) exacte. Fréquence 1000 Hz et diminution du volume bien relevées."),
            "B1": (2.00, 2.0, "Sans faute : distinction binaire vs continu nette, et valeurs 0, 32768, 65535 parfaitement restituées."),
            "B2": (0.50, 2.0, "Formule f = 1/T juste, mais attention à l'unité : 2 ms = 0.002 s d'où 500 Hz (et non 0.5 Hz)."),
            "C1": (1.25, 3.0, "Boucle for présente, mais oubli des time.sleep(cadence) indispensables pour observer le clignotement."),
            "C2": (4.75, 6.0, "Bonne mise en œuvre générale de la boucle while True, test du bouton et seuils de tension bien posés.")
        },
        "points_forts": "Connaissances matérielles solides (ADC, PWM, niveaux logiques).",
        "axes_progres": "Attention aux conversions d'unités physiques (ms en s) et veiller à temporiser les actions dans les fonctions.",
        "conseil": "Ensemble tout à fait encourageant, consolidez l'algorithmique."
    },
    {
        "rang": 7,
        "nom": "HAILLOT",
        "note": 11.75,
        "mention": "Passable",
        "scores": {
            "A1": (0.75, 3.0, "Logique inversée comprise (0=appui), mais rôle du pull-up et de la boucle interne très confus."),
            "A2": (4.00, 4.0, "Sans faute remarquable : justification limpide des 3 itérations et calcul du rapport cyclique 32768/2 = 16384 (25%)."),
            "B1": (0.25, 2.0, "Exercice quasi non traité, manque les valeurs caractéristiques du CAN."),
            "B2": (1.00, 2.0, "Calcul de fréquence 500 Hz parfait avec une gestion exemplaire des puissances de dix (2 x 10^-3 s)."),
            "C1": (0.25, 3.0, "Syntaxe de fonction non acquise (paramètres codés en dur à l'intérieur)."),
            "C2": (5.50, 6.0, "Très belle boucle while True : l'un des seuls à avoir écrit toutes les plages, la coupure générale, le buzzer proportionnel et le cadencement !")
        },
        "points_forts": "Très bonnes aptitudes pratiques en programmation embarquée (Exercice C.2 parmi les meilleurs du groupe).",
        "axes_progres": "Consolider impérativement les définitions de cours (pull-up, ADC) et l'écriture de fonctions réutilisables.",
        "conseil": "Du potentiel pratique indéniable, il faut désormais soigner la théorie."
    },
    {
        "rang": 8,
        "nom": "YACOUBI",
        "note": 11.25,
        "mention": "Passable",
        "scores": {
            "A1": (1.75, 3.0, "Logique PULL_UP bien comprise (repos à 1, appui à 0). Rôle de la boucle interne compris dans les grandes lignes."),
            "A2": (2.75, 4.0, "Coupure sonore par duty_u16(0) bien identifiée. Attention : la boucle s'exécute 3 fois (300, 500, 700) et non 2 fois."),
            "B1": (0.75, 2.0, "Les 3 valeurs de quantification (0, 32768, 65535) sont exactes. Distinction binaire vs analogique à préciser."),
            "B2": (2.00, 2.0, "Sans faute : calcul de fréquence (500 Hz) et rapport cyclique (25%) menés avec succès."),
            "C1": (0.50, 3.0, "Attention : ne pas appeler les variables comme des fonctions (nb_bips() au lieu de for i in range(nb_bips))."),
            "C2": (3.50, 6.0, "Bonne configuration matérielle. La boucle while True est entamée mais n'a pas pu être terminée par manque de temps.")
        },
        "points_forts": "Bonne maîtrise des calculs physiques PWM et des configurations d'entrées/sorties.",
        "axes_progres": "Revoir la syntaxe des boucles for et s'entraîner à coder plus vite pour finir les sujets.",
        "conseil": "Résultats convenables, intensifiez l'entraînement sur machine."
    },
    {
        "rang": 9,
        "nom": "CURTAT",
        "note": 10.75,
        "mention": "Passable",
        "scores": {
            "A1": (1.00, 3.0, "A bien retenu que le bouton renvoie 1 au repos. Rôle de la résistance et de la boucle anti-rebond non compris."),
            "A2": (2.00, 4.0, "Bonne explication de la coupure sonore. Attention : a confondu la borne 300 avec le nombre d'itérations."),
            "B1": (0.75, 2.0, "Mentionne le signal binaire 0 et 1. Valeurs du potentiomètre non indiquées."),
            "B2": (0.50, 2.0, "Formule f = 1/T juste, mais attention à l'erreur d'unité : 2 ms = 0.002 s (donne 500 Hz et non 0.5 Hz)."),
            "C1": (2.75, 3.0, "Très belle écriture de la fonction réutilisable : boucle for, alternance allumage/extinction et temporisations parfaites."),
            "C2": (3.75, 6.0, "Structure générale bien posée. Attention à la syntaxe val = pot.read_u16() et à ne pas utiliser de boucles while bloquantes.")
        },
        "points_forts": "Excellente écriture algorithmique sur l'Exercice C.1.",
        "axes_progres": "Vigilance sur les conversions d'unités physiques et éviter les boucles while à l'intérieur d'un état.",
        "conseil": "Moyenne atteinte, le travail sur la fonction montre de vraies capacités."
    },
    {
        "rang": 10,
        "nom": "RUGGIERO",
        "note": 10.25,
        "mention": "Passable",
        "scores": {
            "A1": (1.50, 3.0, "Traduction 0 = appui exacte en PULL_UP. Rôle de la boucle interne à préciser."),
            "A2": (2.25, 4.0, "Arrêt sonore par duty_u16(0) bien vu. A identifié les 25% et 50%, mais attention à ne pas confondre fréquence et volume."),
            "B1": (1.00, 2.0, "Distinction numérique (0/1) vs analogique variable comprise."),
            "B2": (1.75, 2.0, "Calcul du rapport cyclique à 25% (associé à 16384) parfaitement mené ! Fréquence de 500 Hz trouvée."),
            "C1": (0.50, 3.0, "Confusions de syntaxe sur les paramètres de la fonction."),
            "C2": (3.25, 6.0, "A utilisé des boucles while successives au lieu de if/elif, mais la logique des seuils et du buzzer est comprise.")
        },
        "points_forts": "Bonne intuition sur le rapport cyclique PWM et compréhension générale du cahier des charges.",
        "axes_progres": "Ne jamais utiliser de boucles while pour tester des conditions mutuellement exclusives (utiliser if / elif).",
        "conseil": "Moyenne tout juste atteinte, il faut structurer davantage votre code."
    },
    {
        "rang": 11,
        "nom": "CUBAS",
        "note": 8.75,
        "mention": "Insuffisant",
        "scores": {
            "A1": (1.75, 3.0, "Niveau de repos à 1 et appui à 0 bien identifiés. Rôle de la temporisation trop succinct."),
            "A2": (2.25, 4.0, "Coupure sonore par duty_u16(0) comprise. A oublié la 3e note (700) et s'est trompé sur le calcul de volume (moitié et non double)."),
            "B1": (1.25, 2.0, "Bonne définition de la valeur numérique binaire face à la tension convertie."),
            "B2": (0.50, 2.0, "Formule f = 1/T posée, mais confusion d'unités dans le calcul (1/2000)."),
            "C1": (1.00, 3.0, "Boucle for ébauchée, mais a placé cadence dans le range au lieu de nb_bips, absence de temporisations."),
            "C2": (2.00, 6.0, "Configuration amorcée, mais la boucle while True s'arrête prématurément après la lecture ADC.")
        },
        "points_forts": "Bonne compréhension de la logique Tout-Ou-Rien et du rôle de l'ADC.",
        "axes_progres": "Apprendre à structurer une boucle for d'itération et soigner les conversions d'unités.",
        "conseil": "Des bases présentes, un travail régulier sur machine permettra de progresser."
    },
    {
        "rang": 12,
        "nom": "EROUART",
        "note": 6.50,
        "mention": "Insuffisant",
        "scores": {
            "A1": (1.00, 3.0, "A retenu que 1 correspond au repos. Rôle de la résistance de tirage et de la boucle interne non acquis."),
            "A2": (1.50, 4.0, "Fréquence 1000 Hz trouvée, mais confusion totale sur les valeurs de la boucle (confond arguments et valeurs d'itération)."),
            "B1": (0.75, 2.0, "Intuition du signal constant vs variable. Manque les valeurs de quantification 16 bits."),
            "B2": (0.50, 2.0, "Formule f = 1/T juste, mais erreur d'unité sur les millisecondes (0.5 Hz au lieu de 500 Hz)."),
            "C1": (0.25, 3.0, "Syntaxe invalide : paramètres appelés comme des fonctions, boucle range impossible."),
            "C2": (2.50, 6.0, "Imports et broches initialisés, mais la boucle while True est quasi-vide.")
        },
        "points_forts": "Volonté d'aborder les questions d'analyse matérielle.",
        "axes_progres": "Revoir d'urgence les fondamentaux du langage Python : variables, boucles for et passage de paramètres.",
        "conseil": "Résultats insuffisants. Un travail de reprise méthodique est nécessaire."
    },
    {
        "rang": 13,
        "nom": "LEBLANC",
        "note": 6.00,
        "mention": "Insuffisant",
        "scores": {
            "A1": (1.50, 3.0, "Logique active basse bien comprise (0 à l'appui). Rôle du pull-up vague."),
            "A2": (3.75, 4.0, "Très bonne analyse PWM : 3 itérations (300, 500, 700), coupure sonore et fréquence 1000 Hz exactes."),
            "B1": (0.25, 2.0, "Partie quasi-vierge."),
            "B2": (0.50, 2.0, "Formule posée, mais erreur d'unité (0.5 Hz au lieu de 500 Hz)."),
            "C1": (0.00, 3.0, "Exercice laissé vierge."),
            "C2": (0.00, 6.0, "Exercice laissé vierge.")
        },
        "points_forts": "Très bon démarrage sur l'analyse de code (Partie A bien menée).",
        "axes_progres": "Gestion du temps critique : 9 points abandonnés sans réponse sur la partie programmation.",
        "conseil": "Le début montre que vous pouvez réussir. Entraînez-vous à coder plus rapidement."
    },
    {
        "rang": 14,
        "nom": "MARTIN",
        "note": 5.75,
        "mention": "Insuffisant",
        "scores": {
            "A1": (1.00, 3.0, "A retenu l'activation à 0, mais rôle matériel du pull-up et de la boucle interne non compris."),
            "A2": (1.25, 4.0, "Confusions dans l'analyse de boucle : confond les valeurs de notes avec les rapports cycliques PWM 32768 et 16384."),
            "B1": (0.25, 2.0, "Donne des volts au lieu de la quantification numérique 16 bits."),
            "B2": (1.25, 2.0, "Rapport cyclique de 25% bien noté. Erreur d'unité sur la fréquence (0.5 Hz)."),
            "C1": (0.00, 3.0, "Exercice non abordé."),
            "C2": (2.00, 6.0, "A codé un chenillard de LEDs sur bouton au lieu du cahier des charges des seuils analogiques.")
        },
        "points_forts": "Tentative de programmation d'une séquence de LEDs.",
        "axes_progres": "Lire attentivement les cahiers des charges et revoir les notions de boucle et de quantification ADC.",
        "conseil": "Des lacunes importantes. Prenez le temps de reprendre les TP pas à pas."
    },
    {
        "rang": 15,
        "nom": "ALDARADE",
        "note": 5.25,
        "mention": "Insuffisant",
        "scores": {
            "A1": (1.25, 3.0, "A retenu que l'appui correspond à 0. Rôle du pull-up confus."),
            "A2": (2.00, 4.0, "Arrêt sonore par duty_u16(0) compris, fréquence 1000 Hz trouvée."),
            "B1": (0.75, 2.0, "Mentionne la plage 0V à 3.3V, mais ne donne pas les valeurs de conversion numérique."),
            "B2": (0.50, 2.0, "Formule f = 1/T posée, mais erreur de conversion sur les millisecondes (0.5 Hz)."),
            "C1": (0.75, 3.0, "Allumage et extinction ébauchés, mais pas de boucle for complète ni de paramètres fonctionnels."),
            "C2": (0.00, 6.0, "Exercice non abordé.")
        },
        "points_forts": "Quelques notions de base retenues sur le buzzer et le bouton.",
        "axes_progres": "L'ensemble de la programmation en MicroPython (boucle while True, fonctions, tests conditionnels) est à acquérir.",
        "conseil": "Résultats très fragiles. N'hésitez pas à solliciter de l'aide lors des séances de travaux pratiques."
    }
]

def build_fiches_pdf(filename="Fiches_Individuelles_Eleves_BTS_CIEL.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()

    style_header_ecole = ParagraphStyle(
        'HeaderEcole',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0b3c5d'),
        alignment=TA_CENTER
    )

    style_titre_fiche = ParagraphStyle(
        'TitreFiche',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0b3c5d'),
        alignment=TA_CENTER
    )

    style_soustitre = ParagraphStyle(
        'SousTitre',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569'),
        alignment=TA_CENTER
    )

    style_cell_head = ParagraphStyle(
        'CellHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0b3c5d')
    )

    style_cell_head_center = ParagraphStyle(
        'CellHeadCenter',
        parent=style_cell_head,
        alignment=TA_CENTER
    )

    style_cell = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1e293b')
    )

    style_cell_center = ParagraphStyle(
        'CellTextCenter',
        parent=style_cell,
        alignment=TA_CENTER
    )

    style_cell_bold_center = ParagraphStyle(
        'CellBoldCenter',
        parent=style_cell,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )

    style_comm = ParagraphStyle(
        'CommText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor('#334155')
    )

    style_bilan_titre = ParagraphStyle(
        'BilanTitre',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#0b3c5d')
    )

    story = []

    for idx, e in enumerate(FICHES):
        # -------------------------------------------------------------
        # EN-TÊTE DE LA FICHE
        # -------------------------------------------------------------
        story.append(Paragraph("BTS CIEL 1 — SYSTÈMES NUMÉRIQUES &amp; ÉLECTRONIQUE EMBARQUÉE", style_header_ecole))
        story.append(Paragraph("ÉVALUATION ÉCRITE : INTERFAÇAGE MATÉRIEL &amp; MICROPYTHON (RP2040)", style_soustitre))
        story.append(Spacer(1, 4))
        story.append(Paragraph("FICHE INDIVIDUELLE DE CORRECTION &amp; DE RESTITUTION", style_titre_fiche))
        story.append(Spacer(1, 10))

        # -------------------------------------------------------------
        # BANDEAU IDENTITÉ DE L'ÉLÈVE & NOTE FINALE
        # -------------------------------------------------------------
        if e["note"] >= 16:
            c_badge = "#15803d"
        elif e["note"] >= 12:
            c_badge = "#0284c7"
        elif e["note"] >= 10:
            c_badge = "#d97706"
        else:
            c_badge = "#b91c1c"

        id_data = [
            [
                Paragraph(f"<b>ÉLÈVE :</b> <font size=12 color='#0b3c5d'><b>{e['nom']}</b></font>", style_cell),
                Paragraph(f"<b>RANG :</b> <b>{e['rang']} / 15</b>", style_cell_center),
                Paragraph(f"<b>NOTE FINALE :</b> <font size=14 color='{c_badge}'><b>{e['note']:.2f} / 20</b></font>", style_cell_center)
            ],
            [
                Paragraph(f"<b>Promotion :</b> BTS CIEL 1re Année | Durée : 1h30", style_cell),
                Paragraph(f"<b>Mention :</b> <font color='{c_badge}'><b>{e['mention']}</b></font>", style_cell_center),
                Paragraph("<b>Moyenne de classe :</b> 11,63 / 20", style_cell_center)
            ]
        ]
        t_id = Table(id_data, colWidths=[8.0*cm, 4.5*cm, 5.5*cm])
        t_id.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#0b3c5d')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t_id)
        story.append(Spacer(1, 12))

        # -------------------------------------------------------------
        # TABLEAU DÉTAILLÉ DES POINTS ET COMMENTAIRES PAR EXERCICE
        # -------------------------------------------------------------
        headers_table = [
            Paragraph("<b>Partie / Exercice</b>", style_cell_head),
            Paragraph("<b>Compétences Évaluées</b>", style_cell_head),
            Paragraph("<b>Barème</b>", style_cell_head_center),
            Paragraph("<b>Note</b>", style_cell_head_center),
            Paragraph("<b>Observations &amp; Analyse des Erreurs</b>", style_cell_head)
        ]

        rows_exo = [headers_table]
        
        exos_def = [
            ("Partie A<br/>Ex A.1", "Entrées TOR &amp; Pull-Up", "3.0", e["scores"]["A1"][0], e["scores"]["A1"][2]),
            ("Partie A<br/>Ex A.2", "Analyse Modulaire &amp; PWM", "4.0", e["scores"]["A2"][0], e["scores"]["A2"][2]),
            ("Partie B<br/>Ex B.1", "Entrée Analogique (ADC)", "2.0", e["scores"]["B1"][0], e["scores"]["B1"][2]),
            ("Partie B<br/>Ex B.2", "Signal PWM, Période &amp; Duty", "2.0", e["scores"]["B2"][0], e["scores"]["B2"][2]),
            ("Partie C<br/>Ex C.1", "Fonction Paramétrée &amp; Boucle for", "3.0", e["scores"]["C1"][0], e["scores"]["C1"][2]),
            ("Partie C<br/>Ex C.2", "Mini-Projet Surveillance Multicapteurs", "6.0", e["scores"]["C2"][0], e["scores"]["C2"][2]),
        ]

        for code_exo, nom_comp, bareme, note_obtenue, comm in exos_def:
            rows_exo.append([
                Paragraph(f"<b>{code_exo}</b>", style_cell),
                Paragraph(nom_comp, style_cell),
                Paragraph(f"/{bareme}", style_cell_center),
                Paragraph(f"<b>{note_obtenue:.2f}</b>", style_cell_bold_center),
                Paragraph(comm, style_comm)
            ])

        t_exos = Table(rows_exo, colWidths=[2.2*cm, 4.0*cm, 1.4*cm, 1.4*cm, 9.0*cm])
        t_exos.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0b3c5d')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        story.append(t_exos)
        story.append(Spacer(1, 14))

        # -------------------------------------------------------------
        # SYNTHÈSE PÉDAGOGIQUE & CONSEIL DU PROFESSEUR
        # -------------------------------------------------------------
        bilan_data = [
            [
                Paragraph("<b>POINTS FORTS DÉMONTRÉS</b>", style_bilan_titre),
                Paragraph("<b>AXES DE PROGRÈS PRIORITAIRES</b>", style_bilan_titre)
            ],
            [
                Paragraph(f"• {e['points_forts']}", style_cell),
                Paragraph(f"• {e['axes_progres']}", style_cell)
            ],
            [
                Paragraph("<b>CONSEIL PERSONNALISÉ DE L'ENSEIGNANT :</b>", style_bilan_titre),
                ""
            ],
            [
                Paragraph(f"<i>« {e['conseil']} »</i>", style_cell),
                ""
            ]
        ]
        t_bilan = Table(bilan_data, colWidths=[9.0*cm, 9.0*cm])
        t_bilan.setStyle(TableStyle([
            ('SPAN', (0,2), (1,2)),
            ('SPAN', (0,3), (1,3)),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#f1f5f9')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0b3c5d')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t_bilan)

        # Saut de page pour que chaque élève ait exactement sa page A4 dédiée
        if idx != len(FICHES) - 1:
            story.append(PageBreak())

    doc.build(story)
    print(f"[SUCCÈS] Document PDF généré : {filename} ({len(FICHES)} pages)")

if __name__ == "__main__":
    build_fiches_pdf("c:\\Users\\vince\\OneDrive\\Documents\\GitHub\\cours_bts_ciel1\\Fiches_Individuelles_Eleves_BTS_CIEL.pdf")
