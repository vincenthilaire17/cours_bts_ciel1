# ==============================================================================
# Bibliothèque MicroPython pour Accéléromètre 3 axes MMA7660FC (Grove)
# Interface : I2C (Adresse par défaut : 0x4C)
# BTS CIEL — Systèmes Numériques & Électronique Embarquée
# ==============================================================================

import time

class MMA7660:
    """
    Pilote MicroPython pour le capteur accéléromètre 3 axes MMA7660FC.
    """
    REG_XOUT = 0x00
    REG_YOUT = 0x01
    REG_ZOUT = 0x02
    REG_TILT = 0x03
    REG_MODE = 0x07
    REG_SR   = 0x08

    def __init__(self, i2c, address=0x4C):
        self.i2c = i2c
        self.address = address
        self.init()

    def init(self):
        """Configure le capteur en mode Standby pour paramétrer la fréquence, puis passe en mode Actif."""
        time.sleep_ms(20)
        # 1. Mode Standby (bit 0 = 0)
        self.i2c.writeto_mem(self.address, self.REG_MODE, b'\x00')
        # 2. Vitesse d'échantillonnage : 16 échantillons/seconde
        self.i2c.writeto_mem(self.address, self.REG_SR, b'\x07')
        # 3. Mode Actif (bit 0 = 1)
        self.i2c.writeto_mem(self.address, self.REG_MODE, b'\x01')
        time.sleep_ms(20)

    def _convertir_complement_a_deux(self, valeur_brute):
        """Convertit la valeur brute 6 bits signée (complément à deux) en entier Python."""
        val = valeur_brute & 0x3F
        if val & 0x20:  # Si le bit de signe (bit 5) est à 1
            return val - 64
        return val

    def get_xyz(self):
        """
        Lit les trois axes d'accélération (X, Y, Z).
        Renvoie un tuple (ax, ay, az) en multiples de g (sensibilité ~21.33 LSB/g).
        """
        donnees = self.i2c.readfrom_mem(self.address, self.REG_XOUT, 3)
        # Répéter la lecture si le bit d'alerte (bit 6) indique une mise à jour en cours
        while (donnees[0] & 0x40) or (donnees[1] & 0x40) or (donnees[2] & 0x40):
            donnees = self.i2c.readfrom_mem(self.address, self.REG_XOUT, 3)

        x = self._convertir_complement_a_deux(donnees[0])
        y = self._convertir_complement_a_deux(donnees[1])
        z = self._convertir_complement_a_deux(donnees[2])

        # Sensibilité typique : 21.33 LSB / g sur la plage ±1.5g
        ax = x / 21.33
        ay = y / 21.33
        az = z / 21.33
        return ax, ay, az

    def get_magnitude(self):
        """Calcule la norme totale de l'accélération en g (au repos = environ 1.0g)."""
        ax, ay, az = self.get_xyz()
        return (ax**2 + ay**2 + az**2)**0.5

    def est_secoue(self, seuil_delta=0.35):
        """
        Détecte une secousse ou un choc par rapport à la pesanteur normale (1.0g).
        Renvoie True si une secousse dépasse le seuil, False sinon.
        """
        mag = self.get_magnitude()
        return abs(mag - 1.0) > seuil_delta
