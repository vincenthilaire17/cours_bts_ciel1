# ==============================================================================
# TP 8 : PICO-POWERDAC — Régulation d'Énergie (LM317 / Zener), PWM Matérielle
#        (TLC555CP) & Acquisition Série Synchrone 12 bits (ADS7816P via SPI)
#
# Filière : BTS CIEL — Option B : Électronique et Réseaux (1re Année — Semestre 2)
# Cible   : Raspberry Pi Pico (RP2040 — MicroPython)
# Fichier : main_powerdac_complet.py (CORRIGÉ ENSEIGNANT COMPLET)
#
# BROCHAGE DU CONVERTISSEUR CAN 12 BITS TI ADS7816P (DIP-8) :
# - Broche 1 (VREF)   : Tension de référence étalon issue du régulateur LM317 (2,50 V)
# - Broche 2 (+In)    : Tension analogique à mesurer (0 V à VREF)
# - Broche 3 (-In)    : Reliée à GND (mesure référencée à la masse)
# - Broche 4 (GND)    : Masse commune générale (AD3 + Pico + LM317 + Varta)
# - Broche 5 (/CS)    : Commandée par GP17 du Pico (Active à l'état BAS)
# - Broche 6 (DOUT)   : Sortie série MSB-first -> Pont 1 kΩ / 2,2 kΩ -> GP16 du Pico
# - Broche 7 (DCLOCK) : Horloge série synchrone commandée par GP18 du Pico
# - Broche 8 (+VCC)   : +5,00 V (Rail V+ de l'Analog Discovery 3 + 100 nF)
# ==============================================================================

from machine import Pin, ADC, PWM
import time

# --- 1. PARAMÈTRES ÉTALONS DU BANC MÉTROLOGIQUE ---
VREF_LM317_V = 2.500     # Tension de référence réglée au LM317 (Partie 1) sur broche 1 (VREF)
VREF_PICO_V  = 3.300     # Rail 3V3 interne du Raspberry Pi Pico (CAN interne RP2040)

# --- 2. INTERFACE SÉRIE SYNCHRONE (SPI / BIT-BANGING PRÉCIS) VERS ADS7816P ---
cs_n   = Pin(17, Pin.OUT, value=1)   # Broche 5 (/CS/SHDN) : repos à 1 (mode veille basse conso)
dclock = Pin(18, Pin.OUT, value=0)   # Broche 7 (DCLOCK)   : horloge série
dout   = Pin(16, Pin.IN)             # Broche 6 (DOUT)     : via pont diviseur 1 kΩ / 2,2 kΩ !

# Comparaison métrologique avec le CAN 12 bits interne du RP2040 (GP26 / ADC0)
adc_interne_pico = ADC(Pin(26))

# --- 3. SORTIES CHAÎNE D'ÉNERGIE (RELAIS GROVE + HACHEUR MOTEUR CC) ---
relais_varta = Pin(15, Pin.OUT, value=0)   # Contacteur Relais Grove (+5 V Powerbank Varta)
pwm_secours  = PWM(Pin(14))                # Commande PWM logicielle (ou validation TLC555)
pwm_secours.freq(1000)
pwm_secours.duty_u16(0)


def lire_ads7816_12bits() -> int:
    """
    Exécute un cycle complet d'acquisition 15 coups d'horloge du TI ADS7816P (datasheet SBAS061) :
    - Front descendant de /CS : démarre l'échantillonnage (Sample & Hold).
    - Coups d'horloge 1 et 2 : phase d'acquisition + sortie du 'Null Bit' (0) sur DOUT.
    - Coups d'horloge 3 à 14 : lecture des 12 bits B11 (MSB) à B0 (LSB) après chaque front ↓.
    - Remontée de /CS à 1    : replace l'ADS7816P en veille basse consommation.
    """
    valeur_12b = 0
    dclock.value(0)
    cs_n.value(0)
    time.sleep_us(5)

    # 1) 2 impulsions d'horloge d'échantillonnage + bit nul (Null Bit)
    for _ in range(2):
        dclock.value(1)
        time.sleep_us(5)
        dclock.value(0)
        time.sleep_us(5)

    # 2) Lecture des 12 bits de poids fort (B11) vers poids faible (B0)
    for _ in range(12):
        dclock.value(1)
        time.sleep_us(5)
        bit_lu = dout.value()
        valeur_12b = (valeur_12b << 1) | (bit_lu & 1)
        dclock.value(0)
        time.sleep_us(5)

    cs_n.value(1)
    return valeur_12b


def convertir_tension_ads7816(code_12b: int, vref: float = VREF_LM317_V) -> float:
    """Calcule la tension mesurée par l'ADS7816P : V_mes = (N / 4096) * V_REF."""
    return (code_12b / 4096.0) * vref


def lire_tension_adc_interne(nb_ech: int = 8) -> tuple:
    """Lit le CAN interne du RP2040 sur GP26 et renvoie (code_12b_equiv, tension_V)."""
    somme = 0
    for _ in range(nb_ech):
        somme += adc_interne_pico.read_u16()
    u16_moy = somme / nb_ech
    code_12b_int = int(round((u16_moy / 65535.0) * 4095.0))
    v_int = (u16_moy / 65535.0) * VREF_PICO_V
    return code_12b_int, v_int


# --- 4. BOUCLE PRINCIPALE DE MÉTROLOGIE & DE COMMANDE « PICO-POWERDAC » ---
print("=" * 78)
print("  BANC MÉTROLOGIQUE PICO-POWERDAC — BTS CIEL Option B (TP 8)")
print(f"  Référence externe LM317 V_REF = {VREF_LM317_V:.3f} V -> Quantum ADS7816 q = {(VREF_LM317_V/4096)*1000:.3f} mV")
print("  Sondez /CS (GP17), DCLOCK (GP18) et DOUT (GP16) à l'Analyseur Logique AD3 !")
print("=" * 78)

try:
    while True:
        # 1. Lecture haute précision sur le convertisseur externe TI ADS7816P
        code_ext = lire_ads7816_12bits()
        v_ext = convertir_tension_ads7816(code_ext, VREF_LM317_V)

        # 2. Lecture comparative sur le CAN interne du Pico (GP26)
        code_int, v_int = lire_tension_adc_interne()
        ecart_mv = (v_ext - v_int) * 1000.0

        # 3. Pilotage de la chaîne de puissance selon la mesure étalonnée ADS7816P
        ratio_consigne = max(0.0, min(1.0, v_ext / VREF_LM317_V))
        consigne_pct = ratio_consigne * 100.0

        if consigne_pct < 10.0:
            relais_varta.value(0)
            pwm_secours.duty_u16(0)
            etat_moteur = "❄️ VEILLE (Relais OFF)"
        else:
            relais_varta.value(1)
            pwm_secours.duty_u16(int(ratio_consigne * 65535))
            etat_moteur = f"⚙️ MARCHE ({consigne_pct:5.1f}%)"

        print(
            f"ADS7816: {code_ext:4d}/4095 ({v_ext:5.3f} V) | "
            f"Pico ADC0: {code_int:4d}/4095 ({v_int:5.3f} V) | "
            f"ΔV={ecart_mv:+6.1f} mV | {etat_moteur}"
        )
        time.sleep_ms(250)

except KeyboardInterrupt:
    pwm_secours.duty_u16(0)
    relais_varta.value(0)
    cs_n.value(1)
    print("\nArrêt propre du banc PICO-POWERDAC.")
