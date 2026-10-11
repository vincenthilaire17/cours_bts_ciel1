# ==============================================================================
# BILAN COMPLET OFFICIEL DE LA CLASSE BTS CIEL 1 — 15 COPIES
# ==============================================================================
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

# Liste exhaustive des 15 élèves
ELEVES_15 = [
    {
        "rang": 1,
        "nom": "DEVIER",
        "prenom": "Rémi",
        "partie_a": 6.50,
        "partie_b": 3.00,
        "partie_c": 9.00,
        "note": 18.50,
        "mention": "Très Bien (Major)",
        "appreciation": "Meilleure copie de la promotion ! Compréhension parfaite des mécanismes temps réel (a calculé que sans boucle anti-répétition le compteur défilerait de 2000 en 2s). Partie C irréprochable avec un sans-faute sur la fonction (3/3) et sur le mini-projet (6/6)."
    },
    {
        "rang": 2,
        "nom": "RICHARD",
        "prenom": "Clément",
        "partie_a": 6.50,
        "partie_b": 2.75,
        "partie_c": 8.75,
        "note": 18.00,
        "mention": "Très Bien",
        "appreciation": "Excellente copie, remarquable en tout point. Analyse de code parfaite, compréhension approfondie des pièges matériels (entrée flottante assimilée à une antenne/touche tactile, boucle anti-répétition). Code complet, indenté et 100% fonctionnel."
    },
    {
        "rang": 3,
        "nom": "TREIBER",
        "prenom": "",
        "partie_a": 6.00,
        "partie_b": 3.75,
        "partie_c": 8.00,
        "note": 17.75,
        "mention": "Très Bien",
        "appreciation": "Magnifique copie ! Presque sans faute sur les calculs matériels PWM et ADC. Fonction C.1 parfaite et mini-projet C.2 très bien structuré avec gestion impeccable des seuils et de la cadence temporelle."
    },
    {
        "rang": 4,
        "nom": "CRIT",
        "prenom": "",
        "partie_a": 6.00,
        "partie_b": 2.75,
        "partie_c": 7.50,
        "note": 16.25,
        "mention": "Très Bien",
        "appreciation": "Très bon devoir, rigoureux et méthodique. Très bonne compréhension de la distinction entre signaux TOR binaires et analogiques continus. L'algorithmique est bien posée et la programmation MicroPython est fluide."
    },
    {
        "rang": 5,
        "nom": "GUILLOT",
        "prenom": "Yaan",
        "partie_a": 5.75,
        "partie_b": 3.00,
        "partie_c": 5.50,
        "note": 14.25,
        "mention": "Bien",
        "appreciation": "Très bon travail d'ensemble. Définition claire des niveaux logiques 0V/3.3V, tableau des valeurs de quantification ADC parfait, bonne analyse PWM. Mini-projet bien engagé sur les plages de détection."
    },
    {
        "rang": 6,
        "nom": "BOUSSAGUET",
        "prenom": "Clément",
        "partie_a": 5.00,
        "partie_b": 2.50,
        "partie_c": 6.00,
        "note": 13.50,
        "mention": "Assez Bien",
        "appreciation": "Bon ensemble, travail sérieux. Les notions matérielles (binaire vs analogique, valeurs ADC 0/32768/65535) sont maîtrisées. Attention aux conversions d'unités physiques (ms en s) et veiller à ne pas omettre les temporisations dans les fonctions."
    },
    {
        "rang": 7,
        "nom": "DIEGO",
        "prenom": "",
        "partie_a": 4.75,
        "partie_b": 1.25,
        "partie_c": 5.75,
        "note": 11.75,
        "mention": "Passable",
        "appreciation": "Moyenne atteinte avec de très belles aptitudes pratiques en programmation : le code du mini-projet C.2 est l'un des plus complets et structurés du groupe. Consolider les définitions théoriques de cours (pull-up, ADC)."
    },
    {
        "rang": 8,
        "nom": "GUILLOD",
        "prenom": "Mathis",
        "partie_a": 4.50,
        "partie_b": 2.75,
        "partie_c": 4.00,
        "note": 11.25,
        "mention": "Passable",
        "appreciation": "Ensemble convenable. Les calculs physiques (fréquence et rapport cyclique PWM) sont maîtrisés sans faute. En revanche, l'écriture de fonctions paramétrées et la méthode .value() sur les broches sont à consolider."
    },
    {
        "rang": 9,
        "nom": "CURTAT",
        "prenom": "Maxime",
        "partie_a": 3.00,
        "partie_b": 1.25,
        "partie_c": 6.50,
        "note": 10.75,
        "mention": "Passable",
        "appreciation": "Moyenne obtenue. Excellente écriture de la fonction paramétrée C.1 (boucle for et sleep bien rythmés). Attention aux confusions d'unités physiques sur la période et à la syntaxe des méthodes (val = pot.read_u16())."
    },
    {
        "rang": 10,
        "nom": "RUGGIERO",
        "prenom": "",
        "partie_a": 3.75,
        "partie_b": 2.75,
        "partie_c": 3.75,
        "note": 10.25,
        "mention": "Passable",
        "appreciation": "Moyenne tout juste atteinte. Calcul du rapport cyclique exact (25%). Attention à ne pas remplacer les structures if/elif par des boucles while successives qui bloquent l'exécution du microcontrôleur."
    },
    {
        "rang": 11,
        "nom": "CUBAS",
        "prenom": "Frédéric",
        "partie_a": 4.00,
        "partie_b": 1.75,
        "partie_c": 3.00,
        "note": 8.75,
        "mention": "Insuffisant",
        "appreciation": "Compréhension correcte de la logique binaire du bouton et de l'extinction PWM. En revanche, confusions d'unités physiques (période en ms) et mini-projet inachevé. Poursuivre l'entraînement sur machine."
    },
    {
        "rang": 12,
        "nom": "EROUART",
        "prenom": "Titouan",
        "partie_a": 2.50,
        "partie_b": 1.25,
        "partie_c": 2.75,
        "note": 6.50,
        "mention": "Insuffisant",
        "appreciation": "Résultats insuffisants. Confusions majeures entre paramètres de fonctions, variables et boucles d'itération. L'écriture algorithmique en Python (boucles for, if/elif, lecture de broches) doit être reprise sur machine."
    },
    {
        "rang": 13,
        "nom": "LEBLANC",
        "prenom": "Noam",
        "partie_a": 5.25,
        "partie_b": 0.75,
        "partie_c": 0.00,
        "note": 6.00,
        "mention": "Insuffisant",
        "appreciation": "Début de devoir prometteur sur l'analyse de code (Partie A bien réussie), mais abandon complet sur la partie programmation C.1 et C.2 laissées vierges. Un manque de temps manifeste qui pénalise lourdement la note."
    },
    {
        "rang": 14,
        "nom": "MARTIN",
        "prenom": "",
        "partie_a": 2.25,
        "partie_b": 1.50,
        "partie_c": 2.00,
        "note": 5.75,
        "mention": "Insuffisant",
        "appreciation": "Des lacunes conceptuelles importantes sur les entrées/sorties numériques, les boucles et les CAN. Le mini-projet est hors-sujet par rapport au cahier des charges des seuils analogiques. Travail de reprise indispensable."
    },
    {
        "rang": 15,
        "nom": "ALDARADE",
        "prenom": "Léo",
        "partie_a": 3.25,
        "partie_b": 1.25,
        "partie_c": 0.75,
        "note": 5.25,
        "mention": "Insuffisant",
        "appreciation": "Résultats fragiles. Quelques notions d'analyse de code amorcées, mais la partie programmation n'a quasiment pas été abordée. Revoir impérativement la structure d'une boucle while True et l'interfaçage des entrées/sorties."
    }
]

def build_pdf(filename="Bilan_Evaluation_MicroPython_BTS_CIEL.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=1.4*cm,
        bottomMargin=1.4*cm
    )

    styles = getSampleStyleSheet()
    
    style_titre_grand = ParagraphStyle(
        'TitreGrand',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=colors.HexColor('#0b3c5d'),
        alignment=TA_CENTER
    )
    
    style_soustitre = ParagraphStyle(
        'SousTitre',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#475569'),
        alignment=TA_CENTER
    )
    
    style_h2 = ParagraphStyle(
        'TitreH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0b3c5d'),
        spaceBefore=8,
        spaceAfter=5
    )

    style_cell = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#1e293b')
    )

    style_cell_center = ParagraphStyle(
        'CellTextCenter',
        parent=style_cell,
        alignment=TA_CENTER
    )

    style_cell_bold = ParagraphStyle(
        'CellTextBold',
        parent=style_cell,
        fontName='Helvetica-Bold'
    )

    style_apprec = ParagraphStyle(
        'ApprecText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # =========================================================================
    # PAGE 1 : SYNTHÈSE GLOBALE DE LA PROMOTION (15 ÉLÈVES)
    # =========================================================================
    story.append(Paragraph("BTS CIEL 1 — SYSTÈMES NUMÉRIQUES &amp; ÉLECTRONIQUE EMBARQUÉE", style_soustitre))
    story.append(Spacer(1, 3))
    story.append(Paragraph("BILAN OFFICIEL DE L'ÉVALUATION ÉCRITE : MICROPYTHON RP2040", style_titre_grand))
    story.append(Spacer(1, 2))
    story.append(Paragraph("Interfaçage Matériel, Événements &amp; Programmation Temps Réel | 15 Copies Corrigées", style_soustitre))
    story.append(Spacer(1, 10))

    # Calcul des statistiques sur les 15 élèves
    notes = [e["note"] for e in ELEVES_15]
    moyenne = sum(notes) / len(notes)
    note_max = max(notes)
    note_min = min(notes)
    reussite = sum(1 for n in notes if n >= 10.0) / len(notes) * 100

    # Tableau des KPI
    data_kpi = [
        [
            Paragraph("<b>Effectif Noté</b>", style_cell_center),
            Paragraph("<b>Moyenne Générale</b>", style_cell_center),
            Paragraph("<b>Note Maximale</b>", style_cell_center),
            Paragraph("<b>Note Minimale</b>", style_cell_center),
            Paragraph("<b>Taux de Réussite (≥ 10)</b>", style_cell_center)
        ],
        [
            Paragraph(f"<font size=13 color='#0b3c5d'><b>15 / 15</b></font>", style_cell_center),
            Paragraph(f"<font size=13 color='#0284c7'><b>{moyenne:.2f} / 20</b></font>", style_cell_center),
            Paragraph(f"<font size=13 color='#15803d'><b>{note_max:.2f} / 20</b></font>", style_cell_center),
            Paragraph(f"<font size=13 color='#b91c1c'><b>{note_min:.2f} / 20</b></font>", style_cell_center),
            Paragraph(f"<font size=13 color='#0b3c5d'><b>{reussite:.1f} %</b> (10/15)</font>", style_cell_center)
        ]
    ]
    t_kpi = Table(data_kpi, colWidths=[3.6*cm, 3.6*cm, 3.6*cm, 3.6*cm, 3.6*cm])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#0b3c5d')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 10))

    # Tableau du classement général des 15 élèves
    story.append(Paragraph("Classement Général &amp; Répartition des Notes par Élève", style_h2))
    
    table_headers = [
        Paragraph("<b>Rang</b>", style_cell_center),
        Paragraph("<b>Nom &amp; Prénom</b>", style_cell_center),
        Paragraph("<b>Partie A<br/>(/7)</b>", style_cell_center),
        Paragraph("<b>Partie B<br/>(/4)</b>", style_cell_center),
        Paragraph("<b>Partie C<br/>(/9)</b>", style_cell_center),
        Paragraph("<b>Note /20</b>", style_cell_center),
        Paragraph("<b>Mention</b>", style_cell_center)
    ]
    
    rows = [table_headers]
    for e in ELEVES_15:
        if e["note"] >= 16:
            badge_mention = f"<font color='#15803d'><b>{e['mention']}</b></font>"
        elif e["note"] >= 12:
            badge_mention = f"<font color='#0284c7'><b>{e['mention']}</b></font>"
        elif e["note"] >= 10:
            badge_mention = f"<font color='#d97706'><b>{e['mention']}</b></font>"
        else:
            badge_mention = f"<font color='#b91c1c'><b>{e['mention']}</b></font>"

        rows.append([
            Paragraph(str(e["rang"]), style_cell_center),
            Paragraph(f"<b>{e['nom']}</b> {e['prenom']}", style_cell),
            Paragraph(f"{e['partie_a']:.2f}", style_cell_center),
            Paragraph(f"{e['partie_b']:.2f}", style_cell_center),
            Paragraph(f"{e['partie_c']:.2f}", style_cell_center),
            Paragraph(f"<b>{e['note']:.2f}</b>", style_cell_center),
            Paragraph(badge_mention, style_cell_center)
        ])

    t_recap = Table(rows, colWidths=[1.3*cm, 6.3*cm, 2.3*cm, 2.3*cm, 2.3*cm, 2.3*cm, 2.4*cm])
    t_recap.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0b3c5d')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(t_recap)
    story.append(Spacer(1, 10))

    # Bilan pédagogique synthétique
    data_bilan = [
        [
            Paragraph("<b>Points Forts Collectifs</b>", style_cell_bold),
            Paragraph("<b>Axes de Remédiation Prioritaires</b>", style_cell_bold)
        ],
        [
            Paragraph("• Excellente compréhension globale du PWM (f = 1/T et duty cycle bien assimilés).<br/>"
                      "• Très bonne mémorisation des constructeurs matériels (Pin.IN, Pin.OUT, PWM, ADC).<br/>"
                      "• Bonne détection de la logique inversée PULL_UP (0 = appui, 1 = repos).", style_cell),
            Paragraph("• Attention aux conversions d'unités physiques (2 ms = 0.002 s et non 2 s).<br/>"
                      "• Ne pas confondre variables numériques et appels de fonctions (cadence() vs time.sleep(cadence)).<br/>"
                      "• Toujours utiliser .value() lors de la lecture d'une broche logique.", style_cell)
        ]
    ]
    t_bilan = Table(data_bilan, colWidths=[9.1*cm, 9.1*cm])
    t_bilan.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_bilan)

    # =========================================================================
    # PAGES INDIVIDUELLES : FICHES ÉLÈVES PAR GROUPE DE 4
    # =========================================================================
    story.append(PageBreak())

    for idx, e in enumerate(ELEVES_15):
        card_data = [
            [
                Paragraph(f"<b>{e['rang']}. {e['nom']} {e['prenom']}</b>", ParagraphStyle('NomEleve', parent=style_h2, fontSize=11, textColor=colors.HexColor('#0b3c5d'))),
                Paragraph(f"<b>NOTE FINALE : <font size=11 color='#0b3c5d'>{e['note']:.2f} / 20</font></b> ({e['mention']})", ParagraphStyle('NoteEleve', parent=style_cell_bold, alignment=TA_RIGHT))
            ],
            [
                Paragraph(f"<b>Détail :</b> Partie A (Analyse) : <b>{e['partie_a']:.2f} / 7</b> | Partie B (Matériel &amp; PWM) : <b>{e['partie_b']:.2f} / 4</b> | Partie C (Code) : <b>{e['partie_c']:.2f} / 9</b>", style_cell),
                ""
            ],
            [
                Paragraph(f"<b>Appréciation pédagogique :</b> {e['appreciation']}", style_apprec),
                ""
            ]
        ]
        t_card = Table(card_data, colWidths=[12.7*cm, 5.5*cm])
        t_card.setStyle(TableStyle([
            ('SPAN', (0, 1), (1, 1)),
            ('SPAN', (0, 2), (1, 2)),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffffff')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('LINEBELOW', (0,0), (-1,0), 0.5, colors.HexColor('#e2e8f0')),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ]))
        
        story.append(t_card)
        story.append(Spacer(1, 8))
        
        # Saut de page tous les 4 élèves pour un rendu équilibré sur 4 pages supplémentaires
        if (idx + 1) % 4 == 0 and idx != len(ELEVES_15) - 1:
            story.append(PageBreak())

    doc.build(story)
    print(f"[SUCCÈS] Document PDF officiel généré pour les 15 élèves : {filename}")

if __name__ == "__main__":
    build_pdf("c:\\Users\\vince\\OneDrive\\Documents\\GitHub\\cours_bts_ciel1\\Bilan_Evaluation_MicroPython_BTS_CIEL.pdf")
