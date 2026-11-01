// ==============================================================================
// TP 9 : PICO-TO-NANO — Du MicroPython au Langage C Embarqué sur Arduino Nano
// Cible   : Arduino Nano v3 (ATmega328P — 16 MHz — Logique 5 V)
// Fichier : sketch_nano_synthese_complete.ino (CORRIGÉ ENSEIGNANT COMPLET)
//
// CONCEPTS MIS EN ŒUVRE :
// 1. Typage statique strict (<stdint.h> : uint8_t, int16_t, uint32_t) & sizeof()
// 2. Structures de contrôle (if/else, switch/case, for, while, do/while)
// 3. Fonctions avec typage de retour et passage par référence (&)
// 4. Machine à États Finis (FSM) énumérée (enum class) & multitâche millis()
// 5. Communication série bidirectionnelle formatée (HEX, BIN, DEC) & parsing
// ==============================================================================

#include <Arduino.h>

// --- AFFECTATION DES BROCHES ARDUINO NANO (BROCHAGE MATÉRIEL) ---
const uint8_t PIN_BP_ACTION   = 2;   // Entrée Bouton Poussoir (D2 / INT0 avec INPUT_PULLUP)
const uint8_t PIN_LED_VERTE   = 3;   // Sortie PWM / Témoin système prêt (D3)
const uint8_t PIN_LED_ROUGE   = 4;   // Sortie Tout-Ou-Rien / Alarme (D4)
const uint8_t PIN_RELAIS      = 8;   // Commande Relais Grove de puissance (D8)
const uint8_t PIN_PWM_MOTEUR  = 9;   // Sortie PWM Timer 1 hacheur TIP31C (D9 : 490 Hz)
const uint8_t PIN_POT_CONSIGNE = A0; // Entrée analogique CAN 10 bits (A0 : 0 à 1023)

// --- 1. DÉFINITION DE LA MACHINE À ÉTATS FINIS (FSM) EN C ÉNUMÉRÉ ---
enum class EtatSysteme : uint8_t {
    ARRET_SECURITE = 0,   // Moteur coupé, Relais ouvert, LED Rouge fixe
    VEILLE_ATTENTE = 1,   // Prêt, Relais ouvert, LED Verte clignotante lente
    MARCHE_ACTIVE  = 2,   // Relais fermé, PWM proportionnelle au potentiomètre
    ALARME_BLOCAGE = 3    // Défaut thermique / sabotage : clignotement rapide
};

// --- 2. VARIABLES GLOBALES AVEC TYPAGE STRICT & GESTION DU TEMPS ---
EtatSysteme etatCourant = EtatSysteme::VEILLE_ATTENTE;

uint32_t dateDerniereMesureMs = 0;   // uint32_t obligatoire pour stocker millis() !
uint32_t dateDernierClignotMs  = 0;
uint16_t compteurCycles        = 0;
uint8_t  consignePwmPct        = 0;   // 0 à 100 %

bool etatLedVerte = false;
bool demandeArretUrgence = false;

// --- 3. FONCTIONS UTILITAIRES : CALCUL DE LA RAM LIBRE (SRAM 2048 OCTETS) ---
int16_t calculerRamLibre() {
    extern int __heap_start, *__brkval;
    int v;
    return (int16_t) (&v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval));
}

// --- 4. FONCTION AVEC RETOUR TYPÉ & PASSAGE DE PARAMÈTRE PAR RÉFÉRENCE (&) ---
// Note : en C, passer par référence '&' permet de modifier la variable d'origine
// sans allouer de mémoire supplémentaire, contrairement au passage par valeur !
float lireConsigneAnalogique(uint16_t &codeCanBrut, float tensionReference = 5.0f) {
    codeCanBrut = analogRead(PIN_POT_CONSIGNE); // CAN 10 bits : 0 à 1023
    float tensionVolts = (codeCanBrut / 1023.0f) * tensionReference;
    return tensionVolts; // Valeur renvoyée typée float (4 octets sur AVR)
}

// --- 5. ROUTINE D'INTERRUPTION MATÉRIELLE (ISR) SUR BOUTON D2 ---
void isrBoutonUrgence() {
    // Bouton câblé vers GND : front descendant = appui
    demandeArretUrgence = true;
}

// --- 6. PARSING DE COMMANDES SÉRIE SANS OBJET String (ÉCONOMIE SRAM) ---
void traiterCommandesSerie() {
    while (Serial.available() > 0) {
        char cmd = (char)Serial.read();
        
        switch (cmd) {
            case 'M': // Ordre de Marche
            case 'm':
                if (etatCourant == EtatSysteme::VEILLE_ATTENTE) {
                    etatCourant = EtatSysteme::MARCHE_ACTIVE;
                    Serial.println(F(">> [COMMANDE SÉRIE] Passage en mode MARCHE"));
                }
                break;

            case 'S': // Ordre de Stop / Arrêt
            case 's':
                etatCourant = EtatSysteme::VEILLE_ATTENTE;
                analogWrite(PIN_PWM_MOTEUR, 0);
                digitalWrite(PIN_RELAIS, LOW);
                Serial.println(F(">> [COMMANDE SÉRIE] Passage en mode VEILLE"));
                break;

            case 'A': // Déclenchement alarme de test
            case 'a':
                etatCourant = EtatSysteme::ALARME_BLOCAGE;
                analogWrite(PIN_PWM_MOTEUR, 0);
                digitalWrite(PIN_RELAIS, LOW);
                Serial.println(F(">> [COMMANDE SÉRIE] 🚨 ALARME MANUELLE DÉCLENCHÉE !"));
                break;

            case 'R': // Réarmement
            case 'r':
                etatCourant = EtatSysteme::VEILLE_ATTENTE;
                demandeArretUrgence = false;
                Serial.println(F(">> [COMMANDE SÉRIE] 🟢 Système réarmé avec succès"));
                break;

            case '?': // Rapport d'inspection mémoire
                Serial.println(F("--- BILAN MÉMOIRE ATmega328P ---"));
                Serial.print(F("SRAM Libre restante : "));
                Serial.print(calculerRamLibre());
                Serial.println(F(" octets sur 2048"));
                break;

            default:
                // Ignorer les retours chariots '\r' et sauts de ligne '\n'
                if (cmd != '\r' && cmd != '\n') {
                    Serial.print(F("Commande inconnue : '"));
                    Serial.print(cmd);
                    Serial.println(F("' (Tapez M, S, A, R ou ?)"));
                }
                break;
        }
    }
}

// ==============================================================================
// INITIALISATION DU SYSTÈME (setup) — ÉQUIVALENT AU CODE DE DÉMARRAGE PYTHON
// ==============================================================================
void setup() {
    // 1. Initialisation de la communication série à 115200 bauds
    Serial.begin(115200);
    while (!Serial && millis() < 3000); // Attente connexion moniteur série

    // 2. Configuration des entrées/sorties numériques
    pinMode(PIN_BP_ACTION, INPUT_PULLUP); // Résistance de tirage interne 20-50 kΩ
    pinMode(PIN_LED_VERTE, OUTPUT);
    pinMode(PIN_LED_ROUGE, OUTPUT);
    pinMode(PIN_RELAIS, OUTPUT);
    pinMode(PIN_PWM_MOTEUR, OUTPUT);

    // États de repos sécurisés
    digitalWrite(PIN_LED_VERTE, LOW);
    digitalWrite(PIN_LED_ROUGE, LOW);
    digitalWrite(PIN_RELAIS, LOW);
    analogWrite(PIN_PWM_MOTEUR, 0);

    // 3. Attachement de l'interruption externe INT0 (broche D2)
    attachInterrupt(digitalPinToInterrupt(PIN_BP_ACTION), isrBoutonUrgence, FALLING);

    // 4. Bannière d'accueil et diagnostic de démarrage
    Serial.println(F("=================================================================="));
    Serial.println(F("  TP 9 : PICO-TO-NANO — INITIATION AU LANGAGE C EMBARQUÉ"));
    Serial.println(F("  Architecture 8 bits AVR (ATmega328P — 16 MHz — Logique 5 V)"));
    Serial.println(F("=================================================================="));
    
    // Démonstration sizeof() des types primitifs
    Serial.println(F("TAILLES DES TYPES SUR CETTE ARCHITECTURE 8 BITS (sizeof) :"));
    Serial.print(F("  sizeof(bool)          = ")); Serial.print(sizeof(bool));          Serial.println(F(" octet"));
    Serial.print(F("  sizeof(char/uint8_t)  = ")); Serial.print(sizeof(uint8_t));       Serial.println(F(" octet  [0 .. 255]"));
    Serial.print(F("  sizeof(int/int16_t)   = ")); Serial.print(sizeof(int));           Serial.println(F(" octets [-32768 .. +32767] (SUR PICO = 4 !)"));
    Serial.print(F("  sizeof(long/uint32_t) = ")); Serial.print(sizeof(uint32_t));      Serial.println(F(" octets (requis pour millis)"));
    Serial.print(F("  sizeof(float)         = ")); Serial.print(sizeof(float));         Serial.println(F(" octets (simple précision IEEE 754)"));
    Serial.print(F("  sizeof(double)        = ")); Serial.print(sizeof(double));        Serial.println(F(" octets (SUR AVR DOUBLE = FLOAT = 4 OCTETS !)"));
    Serial.println(F("------------------------------------------------------------------"));
    Serial.println(F("Commandes console : M (Marche) | S (Stop) | A (Alarme) | R (Réarm) | ?"));
    Serial.println(F("=================================================================="));
}

// ==============================================================================
// BOUCLE PRINCIPALE PERPÉTUELLE (loop) — ÉQUIVALENT DU while True: EN PYTHON
// ==============================================================================
void loop() {
    uint32_t tempsActuelMs = millis();

    // --- 1. GESTION DES DEMANDES PRIORITAIRES DE L'ISR ---
    if (demandeArretUrgence && etatCourant != EtatSysteme::ARRET_SECURITE) {
        etatCourant = EtatSysteme::ARRET_SECURITE;
        analogWrite(PIN_PWM_MOTEUR, 0);
        digitalWrite(PIN_RELAIS, LOW);
        Serial.println(F("🚨 [ISR MATÉRIELLE] ARRÊT D'URGENCE COUP-DE-POING DÉCLENCHÉ !"));
    }

    // --- 2. TRAITEMENT DES ORDRES SUR LA CONSOLE SÉRIE ---
    traiterCommandesSerie();

    // --- 3. EXÉCUTION DE LA MACHINE À ÉTATS FINIS (FSM) ---
    uint16_t codeCan = 0;
    float tensionPot = lireConsigneAnalogique(codeCan); // Passage par référence de codeCan !

    switch (etatCourant) {
        case EtatSysteme::ARRET_SECURITE:
            digitalWrite(PIN_LED_ROUGE, HIGH);
            digitalWrite(PIN_LED_VERTE, LOW);
            digitalWrite(PIN_RELAIS, LOW);
            analogWrite(PIN_PWM_MOTEUR, 0);
            consignePwmPct = 0;
            // Réarmement possible par frappe de 'R' sur la console ou double appui
            break;

        case EtatSysteme::VEILLE_ATTENTE:
            digitalWrite(PIN_LED_ROUGE, LOW);
            digitalWrite(PIN_RELAIS, LOW);
            analogWrite(PIN_PWM_MOTEUR, 0);
            consignePwmPct = 0;

            // Clignotement lent de la LED verte (période 1000 ms -> bascule toutes les 500 ms)
            if (tempsActuelMs - dateDernierClignotMs >= 500) {
                dateDernierClignotMs = tempsActuelMs;
                etatLedVerte = !etatLedVerte;
                digitalWrite(PIN_LED_VERTE, etatLedVerte ? HIGH : LOW);
            }

            // Transition automatique en MARCHE si potentiomètre > 15 %
            if (tensionPot >= 0.75f) {
                etatCourant = EtatSysteme::MARCHE_ACTIVE;
                Serial.println(F(">> [TRANSITION FSM] Seuil franchi -> Passage en MARCHE"));
            }
            break;

        case EtatSysteme::MARCHE_ACTIVE:
            digitalWrite(PIN_LED_ROUGE, LOW);
            digitalWrite(PIN_LED_VERTE, HIGH); // Verte fixe
            digitalWrite(PIN_RELAIS, HIGH);    // Contacteur puissance fermé

            // Calcul du rapport PWM (0 à 255) proportionnel à la tension (0 à 5V)
            consignePwmPct = (uint8_t)((tensionPot / 5.0f) * 100.0f);
            {
                uint8_t valeurPwm8b = (uint8_t)map(codeCan, 0, 1023, 0, 255);
                analogWrite(PIN_PWM_MOTEUR, valeurPwm8b);
            }

            // Retour en veille si potentiomètre ramené sous 0.3 V
            if (tensionPot < 0.30f) {
                etatCourant = EtatSysteme::VEILLE_ATTENTE;
                Serial.println(F(">> [TRANSITION FSM] Potentiomètre à 0 -> Retour en VEILLE"));
            }
            break;

        case EtatSysteme::ALARME_BLOCAGE:
            digitalWrite(PIN_RELAIS, LOW);
            analogWrite(PIN_PWM_MOTEUR, 0);
            consignePwmPct = 0;

            // Clignotement rapide en opposition de phase des deux LEDs (100 ms)
            if (tempsActuelMs - dateDernierClignotMs >= 100) {
                dateDernierClignotMs = tempsActuelMs;
                etatLedVerte = !etatLedVerte;
                digitalWrite(PIN_LED_VERTE, etatLedVerte ? HIGH : LOW);
                digitalWrite(PIN_LED_ROUGE, etatLedVerte ? LOW : HIGH);
            }
            break;
    }

    // --- 4. TÂCHE PÉRIODIQUE NON BLOQUANTE (ÉMISSION TÉLÉMÉTRIE TOUTES LES 500 MS) ---
    if (tempsActuelMs - dateDerniereMesureMs >= 500) {
        dateDerniereMesureMs = tempsActuelMs;
        compteurCycles++;

        // Affichage formaté démontrant les différents modificateurs de Serial.print()
        Serial.print(F("[#"));
        if (compteurCycles < 10) Serial.print('0');
        Serial.print(compteurCycles);
        Serial.print(F(" | "));
        Serial.print(tempsActuelMs / 1000.0f, 2);
        Serial.print(F("s] "));

        // Affichage de l'état
        Serial.print(F("État: "));
        switch (etatCourant) {
            case EtatSysteme::ARRET_SECURITE: Serial.print(F("ARRÊT ")); break;
            case EtatSysteme::VEILLE_ATTENTE: Serial.print(F("VEILLE")); break;
            case EtatSysteme::MARCHE_ACTIVE:  Serial.print(F("MARCHE")); break;
            case EtatSysteme::ALARME_BLOCAGE: Serial.print(F("ALARME")); break;
        }

        // Télémétrie analogique
        Serial.print(F(" | A0: "));
        Serial.print(codeCan);
        Serial.print(F("/1023 ("));
        Serial.print(tensionPot, 2);
        Serial.print(F("V) | PWM: "));
        Serial.print(consignePwmPct);
        Serial.print(F("% | RAM: "));
        Serial.print(calculerRamLibre());
        Serial.println(F("o"));
    }
}
