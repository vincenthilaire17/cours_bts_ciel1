# ==============================================================================
# TP 5 : PICO-DRIVEBENCH — PROGRAMME COMPLET DE RÉFÉRENCE (CORRIGÉ PROFESSEUR - 5H)
# Cible : Raspberry Pi Pico (RP2040) — MicroPython
# Périphériques :
#   - Potentiomètre 10 kΩ (TI myParts Kit) entre 3V3 et GND -> Curseur sur GP26 (ADC0 / Port A0)
#   - Module Seeed Grove - Relay v1.2 -> Port D16 (GP16) [Contacteur maître +5V Powerbank Varta]
#   - Transistor NPN TIP31C (TI myParts Kit) + R_B = 330 Ω -> Port D18 (GP18 PWM 1 kHz)
#   - Diode de roue libre 1N4001 aux bornes du moteur CC jaune 3-6V (Cathode au +5V Varta)
#   - Voyants Breadboard : LED Rouge (+ 330 Ω) sur GP20, LED Verte (+ 330 Ω) sur GP21
# ==============================================================================

from machine import Pin, ADC, PWM
import time

# --- CONFIGURATION MATÉRIELLE ---
potentiometre = ADC(Pin(26))          # Entrée analogique 0..3.3V (lecture 0..65535)
relais_secu   = Pin(16, Pin.OUT)      # Contacteur de ligne Partie Puissance (+5V Varta)
led_rouge     = Pin(20, Pin.OUT)      # Voyant Arrêt Sécurisé
led_verte     = Pin(21, Pin.OUT)      # Voyant Variateur PWM Actif

pwm_moteur = PWM(Pin(18))             # Pilotage Base du transistor TIP31C
pwm_moteur.freq(1000)                 # Fréquence MLI / PWM = 1 000 Hz (période 1 ms)
pwm_moteur.duty_u16(0)

# --- PARAMÈTRES D'HYSTÉRÉSIS ANTI-BATTEMENT DU RELAIS ---
SEUIL_MARCHE_PCT = 12.0               # Enclenchement du relais au-dessus de 12 %
SEUIL_ARRET_PCT  = 8.0                # Coupure du relais en dessous de 8 %

# --- ÉTAT INITIAL SÉCURISÉ ---
puissance_autorisee = False
relais_secu.value(0)
led_rouge.value(1)
led_verte.value(0)

print("=== PICO-DRIVEBENCH OPÉRATIONNEL (CORRIGÉ COMPLET) ===")
print("Vérifiez : Switch Grove Shield sur 3V3 + Masse GND commune Pico <-> Powerbank Varta !")

while True:
    # 1. Acquisition de la consigne analogique sur 16 bits (0 à 65535)
    val_adc = potentiometre.read_u16()

    # Conversion en pourcentage (0.0 à 100.0 %) et en tension (0.00 à 3.30 V)
    rapport_pct = (val_adc / 65535.0) * 100.0
    tension_pot = (val_adc / 65535.0) * 3.3

    # 2. Hystérésis sur le contacteur Relais Grove (évite les claquements autour du seuil)
    if (not puissance_autorisee) and (rapport_pct >= SEUIL_MARCHE_PCT):
        puissance_autorisee = True
        relais_secu.value(1)
        time.sleep_ms(15)  # Laisse le contact mécanique se stabiliser avant d'appliquer le PWM
        print("[SÉCURITÉ] Relais Grove FERMÉ -> Ligne +5V Varta alimentée")

    elif puissance_autorisee and (rapport_pct <= SEUIL_ARRET_PCT):
        puissance_autorisee = False
        pwm_moteur.duty_u16(0)  # Coupe d'abord le courant via le transistor (ouverture hors charge !)
        time.sleep_ms(10)
        relais_secu.value(0)
        print("[SÉCURITÉ] Relais Grove OUVERT -> Ligne +5V Varta isolée")

    # 3. Pilotage coordonné des voyants et du hacheur à transistor TIP31C
    if puissance_autorisee:
        led_rouge.value(0)
        led_verte.value(1)
        pwm_moteur.duty_u16(val_adc)
    else:
        pwm_moteur.duty_u16(0)
        relais_secu.value(0)
        led_rouge.value(1)
        led_verte.value(0)

    # 4. Télémesure console pour relevés du Compte Rendu Google Docs
    etat_txt = "ON " if puissance_autorisee else "OFF"
    print(f"Pot={tension_pot:4.2f} V | Alpha={rapport_pct:5.1f} % | Relais={etat_txt} | Duty16={val_adc:5d}")
    time.sleep_ms(200)
