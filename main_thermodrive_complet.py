# ==============================================================================
# TP 6 : PICO-THERMODRIVE — PROGRAMME COMPLET DE RÉFÉRENCE (CORRIGÉ PROFESSEUR - 5H)
# Filière : BTS CIEL — Option B : Électronique et Réseaux (1re Année)
# Cible : Raspberry Pi Pico (RP2040) — MicroPython
# Chaîne d'acquisition analogique (TI myParts Kit + Digilent Analog Discovery 3 ±5V) :
#   - Capteur analogique température (Grove Temp Sensor v1.2 / CTN) en 3,3 V
#   - Étage 1 : AOP Suiveur TL072CP (broches 1, 2, 3) -> Adaptation d'impédance
#   - Étage 2 : AOP Non-Inverseur TL072CP (broches 5, 6, 7 ; R1=10k, R2=4,7k -> Av=1,47)
#   - Étage 3 : Filtre Passe-Bas RC (Rf=1kΩ, Cf=100nF, fc=1592 Hz) + Bride Schottky 2x 1N5819 -> GP26 (ADC0)
#   - Étage 4 : Comparateur collecteur ouvert LM311P (seuil 2,75 V, pull-up 4,7kΩ au +3,3V) -> GP17 (IRQ_FALLING)
# Chaîne d'énergie réutilisée du TP 5 :
#   - Relais Grove sur GP16 (Contacteur +5V Powerbank Varta)
#   - Transistor NPN TIP31C + R_B=330Ω sur GP18 (PWM 1 kHz) + 1N4001 + Moteur CC jaune 3-6V
# ==============================================================================

from machine import Pin, ADC, PWM
import time

# --- 1. INITIALISATION MATÉRIELLE ---
can_temp       = ADC(Pin(26))                    # Entrée analogique filtrée & bridée (0..3,30 V)
pin_surchauffe = Pin(17, Pin.IN, Pin.PULL_UP)    # Sortie collecteur ouvert LM311P (/SURCHAUFFE active à 0)

relais_varta   = Pin(16, Pin.OUT)                # Contacteur maître ligne +5V Powerbank Varta
pwm_ventilo    = PWM(Pin(18))                    # Hacheur série TIP31C
pwm_ventilo.freq(1000)                           # Découpage MLI à 1 kHz
pwm_ventilo.duty_u16(0)

# --- 2. SEUILS THERMIQUES DE LA LOI D'ASSERVISSEMENT ---
V_DEMARRAGE = 2.42   # Déclenchement de la ventilation proportionnelle (30 %)
V_ARRET     = 2.38   # Hystérésis d'arrêt complet (0 % + ouverture relais Grove)
V_PLEIN_GAZ = 2.75   # Seuil critique réglé au potentiomètre sur IN+ du LM311P

# --- 3. VARIABLES D'ÉTAT ---
alerte_irq_materielle = False
ventilation_active    = False


def isr_surchauffe(pin):
    """Routine d'interruption matérielle (ISR) sur front descendant du LM311P."""
    global alerte_irq_materielle
    alerte_irq_materielle = True


# Armement de l'interruption matérielle sur front descendant (3,3 V -> 0 V)
pin_surchauffe.irq(trigger=Pin.IRQ_FALLING, handler=isr_surchauffe)


def lire_tension_filtree(nb_echantillons=8):
    """Filtrage numérique par moyenne glissante sur 8 conversions CAN."""
    somme = 0
    for _ in range(nb_echantillons):
        somme += can_temp.read_u16()
        time.sleep_ms(2)
    moy_u16 = somme // nb_echantillons
    return (moy_u16 / 65535.0) * 3.30


print("=== PICO-THERMODRIVE OPÉRATIONNEL (CORRIGÉ COMPLET OPTION B) ===")
print("Vérifiez : Masses GND communes (AD3 <-> Pico <-> Powerbank Varta) + Bride Schottky 1N5819 !")

while True:
    v_mes = lire_tension_filtree()
    lm311_actif = (pin_surchauffe.value() == 0)

    # Acquittement automatique de l'alerte lorsque la température est redescendue avec marge (50 mV)
    if alerte_irq_materielle and (not lm311_actif) and (v_mes < (V_PLEIN_GAZ - 0.05)):
        alerte_irq_materielle = False
        print("[INFO] Température redescendue -> Fin du mode d'urgence LM311P")

    # PRIORITÉ 1 : Sécurité matérielle LM311P déclenchée -> Refroidissement maximal forcé (100 %)
    if alerte_irq_materielle or lm311_actif:
        if not ventilation_active:
            relais_varta.value(1)
            time.sleep_ms(15)
        ventilation_active = True
        relais_varta.value(1)
        rapport_pct = 100.0
        pwm_ventilo.duty_u16(65535)
        mode_txt = "URGENCE LM311 (100%)"

    # PRIORITÉ 2 : Asservissement proportionnel linéaire entre V_DEMARRAGE et V_PLEIN_GAZ
    else:
        if (not ventilation_active) and (v_mes >= V_DEMARRAGE):
            ventilation_active = True
            relais_varta.value(1)
            time.sleep_ms(15)
        elif ventilation_active and (v_mes <= V_ARRET):
            ventilation_active = False
            pwm_ventilo.duty_u16(0)
            time.sleep_ms(10)
            relais_varta.value(0)

        if ventilation_active:
            relais_varta.value(1)
            ratio = (v_mes - V_DEMARRAGE) / (V_PLEIN_GAZ - V_DEMARRAGE)
            ratio = max(0.0, min(1.0, ratio))
            rapport_pct = 30.0 + ratio * 55.0   # Rampe linéaire de 30 % à 85 %
            pwm_ventilo.duty_u16(int((rapport_pct / 100.0) * 65535))
            mode_txt = "REGULATION PROP.   "
        else:
            pwm_ventilo.duty_u16(0)
            relais_varta.value(0)
            rapport_pct = 0.0
            mode_txt = "VEILLE (ARRET 0%)  "

    code_12b = int((v_mes / 3.30) * 4095)
    etat_lm = "/ALRM" if lm311_actif else "OK   "
    print(f"V_ADC={v_mes:.3f} V ({code_12b:4d}/4095) | LM311={etat_lm} | PWM={rapport_pct:5.1f}% | {mode_txt}")
    time.sleep_ms(200)
