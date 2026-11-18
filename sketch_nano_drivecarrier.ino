// ==============================================================================
// TP 5 bis : NANO-DRIVECARRIER — Transition C++ Embarqué, Nano Carrier & Moteur
// BTS CIEL — 1re Année — Option B (Électronique et Réseaux)
// Durée : 3h00
// Cible : Arduino Nano v3 (ATmega328P @ 16 MHz - 5 V) sur Arduino Nano Connector Carrier
// Auteur : Enseignant BTS CIEL 1
// Fichier : sketch_nano_drivecarrier.ino
// ==============================================================================

#include <Arduino.h>
#include <Grove_LED_Bar.h>

// --- AFFECTATION DES BROCHES SUR ARDUINO NANO CONNECTOR CARRIER (ASX00051) ---
// Note : Le switch "5V - 3V3" du Carrier doit impérativement être placé sur "5V" !
const uint8_t PIN_RELAIS       = 2;  // Header JP2 Pin 5 (D2) : Commande Tout-Ou-Rien du Relais
const uint8_t PIN_LED_ETAT     = 4;  // Header JP2 Pin 7 (D4) : LED témoin de marche
const uint8_t PIN_PWM_MOTEUR   = 9;  // Header JP2 Pin 12 (D9 PWM Timer 1) : Base du Transistor TIP31C
const uint8_t PIN_POT_CONSIGNE = A0; // Connecteur Grove J7 (A0/A1) : Consigne Potentiomètre 10 kΩ

// Connexions pour le module Grove - LED Bar :
// - Pin 3 (Fil Jaune : DCKI / Clock) -> Header JP2 Pin 10 (D7)
// - Pin 4 (Fil Blanc : DI / Data)    -> Header JP2 Pin 9 (D6)
// Orientation 0 : 1er segment vert (niveau bas), dernier segment rouge (niveau max)
const uint8_t PIN_LEDBAR_CLK   = 7;
const uint8_t PIN_LEDBAR_DATA  = 6;

// Instanciation de l'afficheur dynamique
Grove_LED_Bar bar(PIN_LEDBAR_CLK, PIN_LEDBAR_DATA, 0, LED_BAR_10);

// Constantes métrologiques et cadencement
const float TENSION_ALIM_CAN = 5.00f;       // Référence de tension nominale (5,00 V)
const uint32_t PERIODE_TELEMETRIE_MS = 250; // Fréquence d'envoi série (4 Hz) non bloquant

// --- PROTOTYPES DES FONCTIONS C++ (MODULARITÉ DU LOGICIEL EMBARQUÉ) ---
void initialiserMateriel();
float lireConsignePotentiometre(uint16_t &codeCanBrut);
uint8_t convertirTensionEnNiveau(float tensionVolts);
void afficherBargraphe(uint8_t niveau);
void commanderEtagePuissance(uint8_t niveau, bool &etatRelais, uint8_t &valeurPwm);
void envoyerTelemetrieSerie(float tension, uint16_t codeCan, uint8_t niveau, bool relais, uint8_t pwm);
void animationAccueilChenillard();

// ==============================================================================
// INITIALISATION DU SYSTÈME (setup)
// ==============================================================================
void setup() {
    initialiserMateriel();
    animationAccueilChenillard();
    Serial.println(F(">> [SYSTEME] Initialisation terminee. En attente de consigne..."));
}

// ==============================================================================
// BOUCLE PRINCIPALE (loop) : ARCHITECTURE ÉPURÉE EN FONCTIONS DÉDIÉES
// ==============================================================================
void loop() {
    static uint32_t dateDerniereTelemetrie = 0;
    
    // Variables locales d'échange entre fonctions
    uint16_t codeCan = 0;
    bool relaisEnclenche = false;
    uint8_t commandePwm = 0;

    // 1. Acquisition de la consigne (Fonction avec passage par référence '&')
    float tensionConsigne = lireConsignePotentiometre(codeCan);

    // 2. Conversion mathématique de la consigne en niveau discret (0 à 10)
    uint8_t niveauVitesse = convertirTensionEnNiveau(tensionConsigne);

    // 3. Actualisation de l'affichage dynamique (Grove - LED Bar)
    afficherBargraphe(niveauVitesse);

    // 4. Pilotage de la puissance (Sécurité Relais + Modulation PWM Transistor)
    commanderEtagePuissance(niveauVitesse, relaisEnclenche, commandePwm);

    // 5. Télémétrie périodique non bloquante sur le Moniteur Série (millis)
    if (millis() - dateDerniereTelemetrie >= PERIODE_TELEMETRIE_MS) {
        dateDerniereTelemetrie = millis();
        envoyerTelemetrieSerie(tensionConsigne, codeCan, niveauVitesse, relaisEnclenche, commandePwm);
    }
}

// ==============================================================================
// DÉFINITIONS DES FONCTIONS C++
// ==============================================================================

/**
 * @brief Configure les broches d'E/S, démarre l'UART et initialise le bargraphe.
 */
void initialiserMateriel() {
    Serial.begin(115200);
    while (!Serial && millis() < 2000); // Attente port USB (max 2s)

    Serial.println(F("========================================================="));
    Serial.println(F("TP 5 bis : NANO-DRIVECARRIER — BTS CIEL 1re Annee (Option B)"));
    Serial.println(F("Microcontroleur : ATmega328P @ 16 MHz | Shield Grove Nano"));
    Serial.println(F("========================================================="));

    // Configuration des broches TOR
    pinMode(PIN_RELAIS, OUTPUT);
    pinMode(PIN_LED_ETAT, OUTPUT);
    pinMode(PIN_PWM_MOTEUR, OUTPUT);

    // États de repos initiaux (Sécurité active : tout coupé)
    digitalWrite(PIN_RELAIS, LOW);
    digitalWrite(PIN_LED_ETAT, LOW);
    analogWrite(PIN_PWM_MOTEUR, 0);

    // Initialisation du driver MY9221 de la LED Bar
    bar.begin();
    bar.setLevel(0);
}

/**
 * @brief Lit le convertisseur analogique-numérique (CAN 10 bits) et calcule la tension.
 * @param codeCanBrut Passage par référence (&) : variable modifiée directement pour renvoyer le code brut.
 * @return float Tension calculée en Volts (0.00 V à 5.00 V).
 */
float lireConsignePotentiometre(uint16_t &codeCanBrut) {
    codeCanBrut = analogRead(PIN_POT_CONSIGNE); // Valeur brute 0 à 1023
    float tension = (codeCanBrut / 1023.0f) * TENSION_ALIM_CAN;
    return tension;
}

/**
 * @brief Échelonne la tension analogique (0 à 5V) en un niveau discret de 0 à 10.
 * @param tensionVolts Tension d'entrée mesurée (0.0 V à 5.0 V).
 * @return uint8_t Niveau de 0 (arrêt complet) à 10 (pleine puissance).
 */
uint8_t convertirTensionEnNiveau(float tensionVolts) {
    // Zone morte en bas d'échelle pour garantir l'arrêt complet
    if (tensionVolts < 0.15f) {
        return 0;
    }
    if (tensionVolts >= 4.90f) {
        return 10;
    }

    // Découpage proportionnel régulier en 10 paliers de 0,5 V
    uint8_t niveau = (uint8_t)((tensionVolts / 5.0f) * 10.0f + 0.5f);
    if (niveau > 10) niveau = 10;
    return niveau;
}

/**
 * @brief Pilote les 10 segments de la LED Bar Grove selon le niveau calculé.
 * @param niveau Nombre de segments à illuminer (0 à 10).
 */
void afficherBargraphe(uint8_t niveau) {
    bar.setLevel(niveau);
}

/**
 * @brief Gère la chaîne de puissance : contacteur relais et hacheur PWM à transistor TIP31C.
 * @param niveau Niveau de vitesse consigné (0 à 10).
 * @param etatRelais Passage par référence (&) : renvoie l'état logique du relais (true = enclenché).
 * @param valeurPwm Passage par référence (&) : renvoie le rapport cyclique calculé (0 à 255).
 */
void commanderEtagePuissance(uint8_t niveau, bool &etatRelais, uint8_t &valeurPwm) {
    if (niveau == 0) {
        // --- ÉTAT ARRÊT / SÉCURITÉ ---
        // 1. Coupure du signal PWM sur la base du TIP31C
        valeurPwm = 0;
        analogWrite(PIN_PWM_MOTEUR, 0);

        // 2. Ouverture physique du contacteur de ligne (Relais Grove)
        etatRelais = false;
        digitalWrite(PIN_RELAIS, LOW);

        // 3. Extinction de la LED de marche
        digitalWrite(PIN_LED_ETAT, LOW);
    } 
    else {
        // --- ÉTAT MARCHE ACTIVE ---
        // 1. Enclenchement du relais de puissance (ligne 5 V Varta sous tension)
        etatRelais = true;
        digitalWrite(PIN_RELAIS, HIGH);

        // 2. Allumage du voyant d'état
        digitalWrite(PIN_LED_ETAT, HIGH);

        // 3. Calcul du rapport cyclique PWM (échelonné de 70 pour vaincre le frottement sec à 255)
        // Niveau 1 -> PWM = 70 (démarrage doux)
        // Niveau 10 -> PWM = 255 (pleine vitesse)
        valeurPwm = (uint8_t)map(niveau, 1, 10, 70, 255);
        analogWrite(PIN_PWM_MOTEUR, valeurPwm);
    }
}

/**
 * @brief Envoie un rapport formaté sur le Moniteur Série pour validation et traçage.
 */
void envoyerTelemetrieSerie(float tension, uint16_t codeCan, uint8_t niveau, bool relais, uint8_t pwm) {
    Serial.print(F("[TELEM] U_pot: "));
    Serial.print(tension, 2);
    Serial.print(F(" V (CAN: "));
    Serial.print(codeCan);
    Serial.print(F("/1023) | Niveau: "));
    Serial.print(niveau);
    Serial.print(F("/10 | Relais: "));
    Serial.print(relais ? F("FERME [ON] ") : F("OUVERT [OFF]"));
    Serial.print(F(" | PWM TIP31C: "));
    Serial.print(pwm);
    Serial.print(F("/255 ("));
    Serial.print((pwm * 100) / 255);
    Serial.println(F(" %)"));
}

/**
 * @brief Petite animation de démarrage au boot du microcontrôleur.
 */
void animationAccueilChenillard() {
    Serial.println(F(">> [AUTOTEST] Test fonctionnel de la Grove - LED Bar..."));
    for (uint8_t i = 0; i <= 10; i++) {
        bar.setLevel(i);
        delay(60);
    }
    for (int8_t i = 10; i >= 0; i--) {
        bar.setLevel(i);
        delay(40);
    }
}
