# ==============================================================================
# TP 7 : PICO-SAFELOCK — Supervision d'un Verrouillage Matériel de Sécurité (74LSxx)
#        Décodage BCD 7-Segments (CD4511BE) & Test d'Injection de Panne Logicielle
#
# Filière : BTS CIEL — Option B : Électronique et Réseaux (1re Année — Semestre 2)
# Cible   : Raspberry Pi Pico (RP2040 — MicroPython)
# Fichier : main_safelock_complet.py (CORRIGÉ ENSEIGNANT COMPLET)
#
# SÉCURITÉ MATÉRIELLE OBLIGATOIRE :
# - La sortie 1Q (broche 5) de la bascule TTL 5 V SN74LS74N NE DOIT JAMAIS être
#   reliée directement sur GP19 du Pico ! Intercaler le pont diviseur 1 kΩ / 2,2 kΩ
#   (V_GP19 ≈ 4,1 V * 2,2 / 3,2 ≈ 2,82 V <= 3,3 V).
# - Le signal PWM (GP18) traverse la porte ET matérielle SN74LS08N (1B=GP18, 1A=1Q)
#   avant d'attaquer l'étage de puissance TIP31C + Moteur CC jaune 5 V Varta.
# ==============================================================================

from machine import Pin, ADC, PWM
import time

# --- 1. ENTRÉES : CONSIGNE ANALOGIQUE & RETOUR DU VERROU MATÉRIEL 74LS74 ---
pot_consigne = ADC(Pin(26))          # Potentiomètre 10 kΩ sur GP26 (ADC0 : 0 à 3,30 V)
pin_verrou_q = Pin(19, Pin.IN)       # Image 3,3 V de 1Q (SN74LS74N broche 5 via pont 1k / 2,2k)

# Entrée de test "Injection de Panne Logicielle" (fil cavalier vers GND ou BP sur GP15)
pin_sim_crash = Pin(15, Pin.IN, Pin.PULL_UP)

# --- 2. SORTIES : CHAÎNE D'ÉNERGIE & AFFICHEUR D'ÉTAT BCD (CD4511BE) ---
relais_varta = Pin(16, Pin.OUT)      # Contacteur Relais Grove (+5 V Powerbank Varta)
relais_varta.value(0)

pwm_moteur = PWM(Pin(18))            # Vers entrée 1B (broche 2) de la porte ET SN74LS08N
pwm_moteur.freq(1000)                # Fréquence de hachage : 1 kHz
pwm_moteur.duty_u16(0)

# Bus BCD 3 bits vers le décodeur CD4511BE (D = broche 6 reliée à GND -> codes 0 à 7)
bcd_a = Pin(20, Pin.OUT)             # Bit A (poids 1) -> broche 7 du CD4511BE
bcd_b = Pin(21, Pin.OUT)             # Bit B (poids 2) -> broche 1 du CD4511BE
bcd_c = Pin(22, Pin.OUT)             # Bit C (poids 4) -> broche 2 du CD4511BE

# --- 3. VARIABLES D'ÉTAT & JOURNALISATION HORODATÉE (IRQ MATÉRIELLE) ---
t_boot_ms = time.ticks_ms()
nb_arrets_urgence = 0
dernier_evenement = "Démarrage supervision PICO-SAFELOCK"
etat_verrou_precedent = pin_verrou_q.value()
crash_cpu_en_cours = False


def afficher_code_bcd(chiffre: int) -> None:
    """Envoie un chiffre de 0 à 7 en BCD sur les entrées C, B, A du CD4511BE."""
    chiffre = max(0, min(7, int(chiffre)))
    bcd_a.value((chiffre >> 0) & 1)
    bcd_b.value((chiffre >> 1) & 1)
    bcd_c.value((chiffre >> 2) & 1)


def isr_changement_verrou(pin: Pin) -> None:
    """Routine d'interruption sur front montant/descendant du verrou matériel 1Q."""
    global nb_arrets_urgence, dernier_evenement, etat_verrou_precedent
    # Si un gel total du CPU est simulé, le logiciel ne réagit volontairement PLUS :
    # seul le câblage matériel 74LS74 + 74LS08 sauve alors le moteur !
    if crash_cpu_en_cours:
        return
    etat_actuel = pin.value()
    if etat_actuel == etat_verrou_precedent:
        return
    etat_verrou_precedent = etat_actuel
    horodatage_s = time.ticks_diff(time.ticks_ms(), t_boot_ms) / 1000.0

    if etat_actuel == 0:
        nb_arrets_urgence += 1
        # Coupure logicielle redondante immédiate (le 74LS08 a déjà coupé le TIP31C en ~18 ns !)
        pwm_moteur.duty_u16(0)
        relais_varta.value(0)
        afficher_code_bcd(0)
        dernier_evenement = f"[{horodatage_s:7.2f}s] 🛑 ARRÊT D'URGENCE MATÉRIEL #{nb_arrets_urgence} (1Q=0)"
    else:
        dernier_evenement = f"[{horodatage_s:7.2f}s] 🟢 RÉARMEMENT MATÉRIEL VALIDÉ (Front ↑ 1CLK -> 1Q=1)"


# Attachement de l'interruption sur les deux fronts de GP19
pin_verrou_q.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=isr_changement_verrou)


def lire_consigne_pct(nb_ech: int = 8) -> tuple:
    """Lit et moyenne 8 échantillons CAN 12 bits ; renvoie (tension_V, consigne_pct)."""
    somme = 0
    for _ in range(nb_ech):
        somme += pot_consigne.read_u16()
    u16_moy = somme / nb_ech
    tension_v = (u16_moy / 65535.0) * 3.30
    pct = (u16_moy / 65535.0) * 100.0
    return tension_v, pct


def simuler_plantage_logiciel(duree_ms: int = 8000) -> None:
    """
    TEST DE SÛRETÉ DE FONCTIONNEMENT (Fault Injection) :
    Force le PWM logiciel à 100 % et bloque volontairement le processeur (boucle + IRQ)
    pendant 8 s pour démontrer à l'Analyseur Logique AD3 que GP18 reste collé à 3,3 V
    tandis que le verrou câblé (SN74LS74N + SN74LS08N) coupe le moteur CC en < 25 ns !
    """
    global crash_cpu_en_cours, etat_verrou_precedent
    print("\n" + "!" * 74)
    print("💥 [FAULT INJECTION] SIMULATION D'UN PLANTAGE CRITIQUE DU MICROCONTRÔLEUR !")
    print("   -> Relais fermé, PWM GP18 COLLÉ à 100 % (3,3 V), BCD = 7, CPU gelé 8 s...")
    print("   👉 ACTION REQUISE : Frappez le bouton ARRÊT D'URGENCE matériel (/1CLR) !")
    print("!" * 74)

    crash_cpu_en_cours = True
    relais_varta.value(1)
    pwm_moteur.duty_u16(65535)
    afficher_code_bcd(7)

    # Blocage volontaire complet pendant 8 secondes (GP18 reste physiquement à 3,3 V !)
    t_debut_crash = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), t_debut_crash) < duree_ms:
        pass

    crash_cpu_en_cours = False
    etat_verrou_precedent = pin_verrou_q.value()
    print("✅ Fin de la simulation de panne logicielle — reprise de la supervision.\n")


# --- 4. BOUCLE PRINCIPALE DE SUPERVISION « PICO-SAFELOCK » ---
print("=" * 74)
print("  SYSTÈME CYBER-PHYSIQUE PICO-SAFELOCK — BTS CIEL Option B (TP 7)")
print("  Codes CD4511 : 0=AU Verrouillé | 1=Veille | 2=Lent | 3=Moyen | 4=Max | 7=Crash")
print("  Astuce Crash-Test : relier brièvement GP15 à GND pour figer le CPU 8 s.")
print("=" * 74)

dernier_message_affiche = ""

try:
    while True:
        # Déclenchement du test d'injection de panne si GP15 est mis à 0 (GND)
        if pin_sim_crash.value() == 0:
            simuler_plantage_logiciel(8000)

        v_pot, consigne_pct = lire_consigne_pct()
        verrou_autorise = (pin_verrou_q.value() == 1)

        if dernier_evenement != dernier_message_affiche:
            print(">>", dernier_evenement)
            dernier_message_affiche = dernier_evenement

        # CAS 1 : Verrou matériel SN74LS74N déclenché (1Q = 0) -> Sécurité prioritaire
        if not verrou_autorise:
            pwm_moteur.duty_u16(0)
            relais_varta.value(0)
            code_7seg = 0
            rapport_applique = 0.0
            statut = "🛑 VERROUILLÉ (AU / 1Q=0 -> Réarmer sur 1CLK)"

        # CAS 2 : Verrou matériel armé (1Q = 1), consigne basse (< 10 %) -> Veille
        elif consigne_pct < 10.0:
            pwm_moteur.duty_u16(0)
            relais_varta.value(0)
            code_7seg = 1
            rapport_applique = 0.0
            statut = "🟢 ARMÉ — VEILLE (Pot < 10%)"

        # CAS 3 : Verrou matériel armé (1Q = 1) et demande de marche active (>= 10 %)
        else:
            relais_varta.value(1)
            rapport_applique = min(100.0, max(25.0, consigne_pct))
            pwm_moteur.duty_u16(int((rapport_applique / 100.0) * 65535))

            if rapport_applique < 50.0:
                code_7seg = 2
                statut = "⚙️ MARCHE VITESSE BASSE"
            elif rapport_applique < 85.0:
                code_7seg = 3
                statut = "⚙️ MARCHE VITESSE MOYENNE"
            else:
                code_7seg = 4
                statut = "🚀 MARCHE PLEINE PUISSANCE"

        afficher_code_bcd(code_7seg)
        print(
            f"1Q={int(verrou_autorise)} | V_pot={v_pot:4.2f}V ({consigne_pct:5.1f}%) "
            f"| PWM={rapport_applique:5.1f}% | 7Seg=[{code_7seg}] | {statut}"
        )
        time.sleep_ms(250)

except KeyboardInterrupt:
    pwm_moteur.duty_u16(0)
    relais_varta.value(0)
    afficher_code_bcd(0)
    print("\nArrêt propre demandé par l'opérateur — sorties coupées.")
