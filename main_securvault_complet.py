# ==============================================================================
# TP 4 : PICO-SECURVAULT — PROGRAMME COMPLET DE RÉFÉRENCE (CORRIGÉ PROFESSEUR - 3H)
# Cible : Raspberry Pi Pico (RP2040) — MicroPython
# Périphériques :
#   - Grove 12-Channel Capacitive Touch Keypad (UART0 : GP0 TX / GP1 RX, 9600 bauds)
#   - Grove Thumb Joystick (ADC0 GP26 / ADC1 GP27)
#   - Grove 16x2 LCD Series JHD1802 (I2C0 : GP8 SDA / GP9 SCL, Addr 0x3E)
#   - Grove Red LED Matrix w/Driver HT16K33 (I2C0 : GP8 SDA / GP9 SCL, Addr 0x70)
#   - Grove Time of Flight Distance Sensor VL53L0X (I2C0 : Addr 0x29) [Bibliothèque vl53l0x.py]
#   - Grove 3-Axis Digital Accelerometer MMA7660 (I2C0 : Addr 0x4C) [Bibliothèque mma7660.py]
# ==============================================================================

from machine import I2C, Pin, UART, ADC
import time
from vl53l0x import VL53L0X
from mma7660 import MMA7660

# --- CONFIGURATION MATÉRIELLE ---
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100000)
uart_clavier = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
joy_x = ADC(Pin(26))
joy_y = ADC(Pin(27))

# --- INSTANCIATION DES BIBLIOTHÈQUES EXISTANTES ---
capteur_tof = VL53L0X(i2c)
accel = MMA7660(i2c)

# --- ADRESSES I2C ---
ADDR_LCD = 0x3E
ADDR_MATRICE = 0x70

# --- MAPPING TOUCHES DU CLAVIER CAPACITIF (ATTiny1616) ---
MAP_TOUCHES = {
    0xE1: '1', 0xE2: '2', 0xE3: '3',
    0xE4: '4', 0xE5: '5', 0xE6: '6',
    0xE7: '7', 0xE8: '8', 0xE9: '9',
    0xEA: '*', 0xEB: '0', 0xEC: '#'
}

# --- MOTIFS GRAPHIQUES 8x8 POUR LA MATRICE LED HT16K33 ---
ICONES = {
    "CADENAS_FERME": [
        0x18, 0x24, 0x24, 0x7E, 0x7E, 0x7E, 0x7E, 0x00
    ],
    "CADENAS_OUVERT": [
        0x0C, 0x12, 0x02, 0x7E, 0x7E, 0x7E, 0x7E, 0x00
    ],
    "ERREUR_X": [
        0x81, 0x42, 0x24, 0x18, 0x18, 0x24, 0x42, 0x81
    ],
    "ETOILE": [
        0x18, 0x99, 0x5A, 0x3C, 0x3C, 0x5A, 0x99, 0x18
    ],
    "ETEINT": [0x00] * 8
}

# --- FONCTIONS PILOTES LCD 16x2 ---
def lcd_commande(cmd):
    i2c.writeto(ADDR_LCD, bytes([0x80, cmd]))

def lcd_init():
    time.sleep_ms(50)
    lcd_commande(0x28)  # Mode 2 lignes 5x8
    lcd_commande(0x0C)  # Affichage ON, curseur OFF
    lcd_commande(0x01)  # Effacer écran
    time.sleep_ms(5)
    lcd_commande(0x06)  # Curseur incrémente

def lcd_effacer():
    lcd_commande(0x01)
    time.sleep_ms(2)

def lcd_afficher_texte(texte, ligne=0, colonne=0):
    adresse_ram = 0x80 + (0x40 * ligne) + colonne
    lcd_commande(adresse_ram)
    for car in texte:
        i2c.writeto(ADDR_LCD, bytes([0x40, ord(car)]))

# --- FONCTIONS PILOTES MATRICE 8x8 (HT16K33) ---
def matrice_init():
    i2c.writeto(ADDR_MATRICE, bytes([0x21]))  # Oscillateur ON
    i2c.writeto(ADDR_MATRICE, bytes([0x81]))  # Display ON, clignotement OFF
    i2c.writeto(ADDR_MATRICE, bytes([0xEF]))  # Luminosité max (0xE0 à 0xEF)

def matrice_afficher(motif_8_octets):
    tampon = bytearray(17)
    tampon[0] = 0x00
    for i in range(8):
        tampon[1 + i * 2] = motif_8_octets[i]
        tampon[2 + i * 2] = 0x00
    i2c.writeto(ADDR_MATRICE, tampon)

# --- FONCTIONS PILOTES ENTRÉES ---
def lire_touche_clavier():
    if uart_clavier.any():
        octet_recu = uart_clavier.read(1)[0]
        return MAP_TOUCHES.get(octet_recu, None)
    return None

def lire_direction_joystick():
    val_x = joy_x.read_u16()
    val_y = joy_y.read_u16()
    if val_x > 52000:
        return "DROITE"
    elif val_x < 14000:
        return "GAUCHE"
    elif val_y > 52000:
        return "HAUT"
    elif val_y < 14000:
        return "BAS"
    return "CENTRE"

# --- CONSTANTES DE LA MACHINE À ÉTATS ---
ETAT_VEILLE            = 0
ETAT_SAISIE_PIN        = 1
ETAT_VERIF_PIN         = 2
ETAT_MENU_ACTIF        = 3
ETAT_OUVERTURE         = 4
ETAT_VERROUILLAGE_TEMP = 5
ETAT_ALARME_SABOTAGE   = 6

# --- VARIABLES D'ÉTAT GLOBALES ---
CODE_SECRET_MAITRE = "1234"
code_en_cours = ""
nb_erreurs = 0
etat_courant = ETAT_VEILLE

t_debut_etat = 0
t_dernier_clignotement = 0
etat_led_croix = True
dernier_affichage_sec = -1

# --- DÉMARRAGE DU SYSTÈME ---
print("=== INITIALISATION PICO-SECURVAULT (VERSION 3H) ===")
lcd_init()
matrice_init()
matrice_afficher(ICONES["CADENAS_FERME"])
lcd_afficher_texte("SECURVAULT PRETS", 0, 0)
lcd_afficher_texte("APPROCHEZ OU PIN", 1, 0)

# --- BOUCLE PRINCIPALE DE LA MACHINE À ÉTATS ---
while True:
    # ------------------------------------------------------------------
    # SURVEILLANCE GLOBALE DU SABOTAGE PHYSIQUE (ACCÉLÉROMÈTRE)
    # ------------------------------------------------------------------
    if etat_courant != ETAT_ALARME_SABOTAGE and accel.est_secoue(seuil_delta=0.4):
        print("[URGENCE] Sabotage détecté par l'accéléromètre MMA7660 !")
        t_debut_etat = time.ticks_ms()
        t_dernier_clignotement = time.ticks_ms()
        etat_led_croix = True
        lcd_effacer()
        lcd_afficher_texte("ALERTE SABOTAGE!", 0, 0)
        lcd_afficher_texte("CHOC DETECTE !  ", 1, 0)
        matrice_afficher(ICONES["ERREUR_X"])
        etat_courant = ETAT_ALARME_SABOTAGE

    # ------------------------------------------------------------------
    # ÉTAT 0 : VEILLE AVEC RÉVEIL OPTIQUE ToF
    # ------------------------------------------------------------------
    elif etat_courant == ETAT_VEILLE:
        # Réveil sans contact par radar ToF laser
        dist = capteur_tof.ping()
        touche = lire_touche_clavier()

        if (dist < 300) or (touche and touche.isdigit()):
            code_en_cours = touche if (touche and touche.isdigit()) else ""
            lcd_effacer()
            lcd_afficher_texte("CODE PIN :      ", 0, 0)
            etoiles = "*" * len(code_en_cours)
            lcd_afficher_texte(etoiles + " " * (16 - len(etoiles)), 1, 0)
            etat_courant = ETAT_SAISIE_PIN

    # ------------------------------------------------------------------
    # ÉTAT 1 : SAISIE EN COURS DU CODE
    # ------------------------------------------------------------------
    elif etat_courant == ETAT_SAISIE_PIN:
        touche = lire_touche_clavier()
        if touche:
            if touche.isdigit() and len(code_en_cours) < 8:
                code_en_cours += touche
                etoiles = "*" * len(code_en_cours)
                lcd_afficher_texte(etoiles + " " * (16 - len(etoiles)), 1, 0)
            elif touche == '*':
                code_en_cours = code_en_cours[:-1]
                etoiles = "*" * len(code_en_cours)
                lcd_afficher_texte(etoiles + " " * (16 - len(etoiles)), 1, 0)
                if len(code_en_cours) == 0:
                    lcd_effacer()
                    matrice_afficher(ICONES["CADENAS_FERME"])
                    lcd_afficher_texte("SECURVAULT PRETS", 0, 0)
                    lcd_afficher_texte("APPROCHEZ OU PIN", 1, 0)
                    etat_courant = ETAT_VEILLE
            elif touche == '#':
                etat_courant = ETAT_VERIF_PIN

    # ------------------------------------------------------------------
    # ÉTAT 2 : VÉRIFICATION DU CODE
    # ------------------------------------------------------------------
    elif etat_courant == ETAT_VERIF_PIN:
        if code_en_cours == CODE_SECRET_MAITRE:
            nb_erreurs = 0
            code_en_cours = ""
            matrice_afficher(ICONES["ETOILE"])
            lcd_effacer()
            lcd_afficher_texte("CODE VALIDE !   ", 0, 0)
            lcd_afficher_texte("BIENVENUE       ", 1, 0)
            time.sleep_ms(1200)
            lcd_effacer()
            lcd_afficher_texte("JOY >: OUVRIR   ", 0, 0)
            lcd_afficher_texte("JOY <: QUITTER  ", 1, 0)
            etat_courant = ETAT_MENU_ACTIF
        else:
            nb_erreurs += 1
            code_en_cours = ""
            matrice_afficher(ICONES["ERREUR_X"])
            lcd_effacer()
            lcd_afficher_texte("CODE INCORRECT !", 0, 0)
            lcd_afficher_texte(f"ESSAIS : {nb_erreurs}/3     ", 1, 0)
            time.sleep_ms(1500)

            if nb_erreurs >= 3:
                t_debut_etat = time.ticks_ms()
                t_dernier_clignotement = time.ticks_ms()
                dernier_affichage_sec = -1
                etat_led_croix = True
                lcd_effacer()
                lcd_afficher_texte("BLOCAGE SECURITE", 0, 0)
                etat_courant = ETAT_VERROUILLAGE_TEMP
            else:
                matrice_afficher(ICONES["CADENAS_FERME"])
                lcd_effacer()
                lcd_afficher_texte("SECURVAULT PRETS", 0, 0)
                lcd_afficher_texte("APPROCHEZ OU PIN", 1, 0)
                etat_courant = ETAT_VEILLE

    # ------------------------------------------------------------------
    # ÉTAT 3 : MENU ACTIF (NAVIGATION JOYSTICK)
    # ------------------------------------------------------------------
    elif etat_courant == ETAT_MENU_ACTIF:
        direction = lire_direction_joystick()
        if direction == "DROITE":
            t_debut_etat = time.ticks_ms()
            matrice_afficher(ICONES["CADENAS_OUVERT"])
            lcd_effacer()
            lcd_afficher_texte("SAS DEVERROUILLE", 0, 0)
            dist_porte = capteur_tof.ping()
            lcd_afficher_texte(f"PORTE : {dist_porte} mm   ", 1, 0)
            etat_courant = ETAT_OUVERTURE
        elif direction == "GAUCHE":
            matrice_afficher(ICONES["CADENAS_FERME"])
            lcd_effacer()
            lcd_afficher_texte("SECURVAULT PRETS", 0, 0)
            lcd_afficher_texte("APPROCHEZ OU PIN", 1, 0)
            etat_courant = ETAT_VEILLE

    # ------------------------------------------------------------------
    # ÉTAT 4 : OUVERTURE SAS (TEMPORISATION 5s)
    # ------------------------------------------------------------------
    elif etat_courant == ETAT_OUVERTURE:
        temps_ecoule = time.ticks_diff(time.ticks_ms(), t_debut_etat)
        if temps_ecoule >= 5000:
            matrice_afficher(ICONES["CADENAS_FERME"])
            lcd_effacer()
            lcd_afficher_texte("SECURVAULT PRETS", 0, 0)
            lcd_afficher_texte("APPROCHEZ OU PIN", 1, 0)
            etat_courant = ETAT_VEILLE

    # ------------------------------------------------------------------
    # ÉTAT 5 : VERROUILLAGE DE SÉCURITÉ (10s NON-BLOQUANT)
    # ------------------------------------------------------------------
    elif etat_courant == ETAT_VERROUILLAGE_TEMP:
        temps_ecoule = time.ticks_diff(time.ticks_ms(), t_debut_etat)
        secondes_restantes = 10 - (temps_ecoule // 1000)

        # Mise à jour de l'affichage du compte à rebours
        if secondes_restantes != dernier_affichage_sec and secondes_restantes >= 0:
            dernier_affichage_sec = secondes_restantes
            lcd_afficher_texte(f"ATTENTE : {secondes_restantes} s    ", 1, 0)

        # Clignotement de la croix 'X' sur la matrice toutes les 300 ms
        if time.ticks_diff(time.ticks_ms(), t_dernier_clignotement) >= 300:
            t_dernier_clignotement = time.ticks_ms()
            etat_led_croix = not etat_led_croix
            matrice_afficher(ICONES["ERREUR_X"] if etat_led_croix else ICONES["ETEINT"])

        # Fin du blocage après 10 secondes
        if temps_ecoule >= 10000:
            nb_erreurs = 0
            matrice_afficher(ICONES["CADENAS_FERME"])
            lcd_effacer()
            lcd_afficher_texte("SECURVAULT PRETS", 0, 0)
            lcd_afficher_texte("APPROCHEZ OU PIN", 1, 0)
            etat_courant = ETAT_VEILLE

    # ------------------------------------------------------------------
    # ÉTAT 6 : ALARME SABOTAGE PHYSIQUE
    # ------------------------------------------------------------------
    elif etat_courant == ETAT_ALARME_SABOTAGE:
        temps_ecoule = time.ticks_diff(time.ticks_ms(), t_debut_etat)

        # Clignotement rapide d'alarme (150 ms)
        if time.ticks_diff(time.ticks_ms(), t_dernier_clignotement) >= 150:
            t_dernier_clignotement = time.ticks_ms()
            etat_led_croix = not etat_led_croix
            matrice_afficher(ICONES["ERREUR_X"] if etat_led_croix else ICONES["ETEINT"])

        # Rétablissement après 5 secondes si le système est stabilisé
        if temps_ecoule >= 5000:
            matrice_afficher(ICONES["CADENAS_FERME"])
            lcd_effacer()
            lcd_afficher_texte("SECURVAULT PRETS", 0, 0)
            lcd_afficher_texte("APPROCHEZ OU PIN", 1, 0)
            etat_courant = ETAT_VEILLE

    time.sleep_ms(15)  # Cadence régulière non-bloquante
