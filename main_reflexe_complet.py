# ==============================================================================
# TP 3 : PICO-RÉFLEXE — PROGRAMME COMPLET DE RÉFÉRENCE (CORRIGÉ PROFESSEUR)
# Cible : Raspberry Pi Pico (RP2040) — MicroPython
# Architecture : Machine à États Finis (FSM)
# Périphériques :
#   - LED Verte   : GP15 (Pin.OUT) -> Signal TOP / Niveau Ninja (< 250 ms)
#   - LED Jaune   : GP14 (Pin.OUT) -> Veille / Niveau Moyen (250-400 ms)
#   - LED Rouge   : GP13 (Pin.OUT) -> Alerte Triche / Trop lent (> 400 ms)
#   - Bouton      : GP18 (Pin.IN, Pin.PULL_DOWN)
#   - Buzzer PWM  : GP16 (PWM)
#   - Potentiomètre : GP26 / ADC0 -> Réglage du seuil de tolérance (300 à 900 ms)
# ==============================================================================

from machine import Pin, PWM, ADC
import time
import random

# --- CONFIGURATION MATÉRIELLE ---
led_verte = Pin(15, Pin.OUT)
led_jaune = Pin(14, Pin.OUT)
led_rouge = Pin(13, Pin.OUT)
bouton = Pin(18, Pin.IN, Pin.PULL_DOWN)
pot = ADC(Pin(26))
buzzer = PWM(Pin(16))
buzzer.duty_u16(0)

# --- DÉFINITION DES ÉTATS DE LA MACHINE (FSM) ---
ETAT_VEILLE            = 0
ETAT_ARMEMENT          = 1
ETAT_ATTENTE_ALEATOIRE = 2
ETAT_CHRONO_REACTION   = 3
ETAT_TRICHE            = 4
ETAT_EVALUATION        = 5
ETAT_FIN_SESSION       = 6

# --- FONCTIONS UTILITAIRES ---
def eteindre_leds():
    """Éteint toutes les LEDs du système."""
    led_verte.value(0)
    led_jaune.value(0)
    led_rouge.value(0)

def bip(frequence, duree_ms, duty=30000):
    """Émet un signal sonore de fréquence et durée données."""
    buzzer.freq(frequence)
    buzzer.duty_u16(duty)
    time.sleep_ms(duree_ms)
    buzzer.duty_u16(0)

def lire_seuil_difficulte():
    """Convertit la valeur ADC du potentiomètre en seuil temporel (300 à 900 ms)."""
    valeur_adc = pot.read_u16()
    return int(300 + (valeur_adc / 65535.0) * 600)

def attendre_relachement_bouton():
    """Empêche les déclenchements parasites si le bouton reste maintenu enfoncé."""
    while bouton.value() == 1:
        time.sleep_ms(10)

def alerte_triche():
    """Déclenche la sanction en cas d'anticipation ou de faux départ."""
    print("[PÉNALITÉ] Faux départ ! Ne pressez pas avant le signal !")
    led_rouge.value(1)
    buzzer.freq(180)        # Fréquence basse et stridente
    buzzer.duty_u16(45000)
    time.sleep_ms(1000)
    buzzer.duty_u16(0)
    led_rouge.value(0)
    attendre_relachement_bouton()

def retour_leds(temps_ms):
    """Indique le niveau de performance à l'aide des LEDs."""
    eteindre_leds()
    if temps_ms < 250:
        print("  -> Niveau : Ninja / Pilote (Excellent !)")
        led_verte.value(1)
    elif temps_ms <= 400:
        print("  -> Niveau : Réflexe standard (Moyen)")
        led_jaune.value(1)
    else:
        print("  -> Niveau : Trop lent")
        led_rouge.value(1)
    time.sleep_ms(1200)
    eteindre_leds()

# --- PROGRAMME PRINCIPAL ---
etat = ETAT_VEILLE
scores = []
nb_triches = 0
manche = 1
delai_ms = 0
t_debut_attente = 0
t_top = 0
seuil_limite = 600

print("=== SYSTÈME PICO-RÉFLEXE INITIALISÉ ===")
eteindre_leds()

while True:
    # ------------------------------------------------------------------
    # ÉTAT 0 : VEILLE
    # ------------------------------------------------------------------
    if etat == ETAT_VEILLE:
        seuil_limite = lire_seuil_difficulte()
        led_jaune.value(1)  # Témoin d'attente / prêt
        
        if bouton.value() == 1:
            attendre_relachement_bouton()
            led_jaune.value(0)
            print(f"\n--- Manche {manche}/5 | Difficulté max : {seuil_limite} ms ---")
            etat = ETAT_ARMEMENT  # Transition

    # ------------------------------------------------------------------
    # ÉTAT 1 : ARMEMENT
    # ------------------------------------------------------------------
    elif etat == ETAT_ARMEMENT:
        bip(440, 150)  # Bip d'armement (La 440 Hz)
        delai_ms = int(random.uniform(2.0, 5.0) * 1000)
        t_debut_attente = time.ticks_ms()
        etat = ETAT_ATTENTE_ALEATOIRE  # Transition immédiate

    # ------------------------------------------------------------------
    # ÉTAT 2 : ATTENTE ALÉATOIRE & SURVEILLANCE ANTI-TRICHE
    # ------------------------------------------------------------------
    elif etat == ETAT_ATTENTE_ALEATOIRE:
        # Détection d'un faux départ (appui prématuré)
        if bouton.value() == 1:
            attendre_relachement_bouton()
            nb_triches += 1
            scores.append(None)       # Manche pénalisée
            etat = ETAT_TRICHE
        # Vérification de l'expiration du délai aléatoire
        elif time.ticks_diff(time.ticks_ms(), t_debut_attente) >= delai_ms:
            etat = ETAT_CHRONO_REACTION

    # ------------------------------------------------------------------
    # ÉTAT 3 : CHRONOMÉTRAGE DU RÉFLEXE (SIGNAL TOP)
    # ------------------------------------------------------------------
    elif etat == ETAT_CHRONO_REACTION:
        led_verte.value(1)
        bip(880, 80)  # Bip aigu de départ "TOP"
        t_top = time.ticks_ms()
        
        temps_reaction = None
        # Attente active de l'appui avec vérification du temps limite
        while time.ticks_diff(time.ticks_ms(), t_top) <= seuil_limite:
            if bouton.value() == 1:
                t_fin = time.ticks_ms()
                temps_reaction = time.ticks_diff(t_fin, t_top)
                attendre_relachement_bouton()
                break
            time.sleep_ms(1)
        
        eteindre_leds()
        
        if temps_reaction is not None:
            print(f"Bravo ! Temps de réaction : {temps_reaction} ms")
            scores.append(temps_reaction)
            retour_leds(temps_reaction)
        else:
            print(f"[TEMPS ÉCOULÉ] Trop lent ! Temps supérieur à {seuil_limite} ms.")
            scores.append(None)
            nb_triches += 1
            # Alerte visuelle et sonore de dépassement de temps
            led_rouge.value(1)
            bip(220, 300)
            time.sleep_ms(500)
            eteindre_leds()
            
        etat = ETAT_EVALUATION

    # ------------------------------------------------------------------
    # ÉTAT 4 : GESTION DE LA TRICHE
    # ------------------------------------------------------------------
    elif etat == ETAT_TRICHE:
        alerte_triche()
        etat = ETAT_EVALUATION

    # ------------------------------------------------------------------
    # ÉTAT 5 : ÉVALUATION ET TRANSITION DE MANCHE
    # ------------------------------------------------------------------
    elif etat == ETAT_EVALUATION:
        manche += 1
        if manche <= 5:
            time.sleep_ms(500)  # Court répit avant la manche suivante
            etat = ETAT_VEILLE
        else:
            etat = ETAT_FIN_SESSION

    # ------------------------------------------------------------------
    # ÉTAT 6 : BILAN COMPLET DE FIN DE SESSION
    # ------------------------------------------------------------------
    elif etat == ETAT_FIN_SESSION:
        print("\n" + "=" * 45)
        print("          BILAN DE LA SESSION (5 MANCHES)")
        print("=" * 45)
        
        # Filtrer uniquement les manches réussies
        temps_valides = [s for s in scores if s is not None]
        
        for idx, score in enumerate(scores, 1):
            if score is not None:
                print(f" Manche {idx} : {score:4d} ms")
            else:
                print(f" Manche {idx} : ÉCHEC / PÉNALITÉ")
        print("-" * 45)
        
        if len(temps_valides) > 0:
            meilleur = min(temps_valides)
            moyenne = sum(temps_valides) / len(temps_valides)
            print(f" Record de la session : {meilleur} ms")
            print(f" Temps moyen          : {moyenne:.1f} ms")
        else:
            print(" Aucune manche valide réussie !")
            
        print(f" Faux départs / Échecs : {nb_triches}")
        print("=" * 45)
        
        # Jingle de fin de session
        bip(523, 100)  # Do5
        time.sleep_ms(50)
        bip(659, 100)  # Mi5
        time.sleep_ms(50)
        bip(784, 250)  # Sol5
        
        print("\nAppuyez sur le bouton pour relancer une partie...")
        while bouton.value() == 0:
            time.sleep_ms(50)
        attendre_relachement_bouton()
        
        # Réinitialisation pour une nouvelle session
        manche = 1
        scores = []
        nb_triches = 0
        etat = ETAT_VEILLE

    time.sleep_ms(5)  # Cadence régulière de la boucle FSM
